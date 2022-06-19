# pylint: disable=missing-function-docstring

import pytest

from fideslib.cryptography.cryptographic_util import hash_with_salt
from fideslib.models.client import ClientDetail, _get_root_client_detail
from fideslib.oauth.scopes import SCOPES


def test_create_client_and_secret(db, config):
    new_client, secret = ClientDetail.create_client_and_secret(
        db,
        config.security.OAUTH_CLIENT_ID_LENGTH_BYTES,
        config.security.OAUTH_CLIENT_SECRET_LENGTH_BYTES,
    )

    assert new_client.hashed_secret is not None
    assert (
        hash_with_salt(
            secret.encode(config.security.ENCODING),
            new_client.salt.encode(config.security.ENCODING),
        )
        == new_client.hashed_secret
    )


def test_get_client(db, oauth_client):
    client = ClientDetail.get(db, object_id=oauth_client.id)
    assert client
    assert client.id == oauth_client.id
    assert client.scopes == SCOPES
    assert oauth_client.hashed_secret == "thisisatest"


def test_get_client_root_client(db, config):
    client = ClientDetail.get(
        db,
        object_id="fidesadmin",
        root_client_id=config.security.OAUTH_ROOT_CLIENT_ID,
        root_client_hash=config.security.OAUTH_ROOT_CLIENT_SECRET_HASH,
        scopes=SCOPES,
    )
    assert client
    assert client.id == config.security.OAUTH_ROOT_CLIENT_ID
    assert client.scopes == SCOPES


def test_credentials_valid(db, config):
    new_client, secret = ClientDetail.create_client_and_secret(
        db,
        config.security.OAUTH_CLIENT_ID_LENGTH_BYTES,
        config.security.OAUTH_CLIENT_SECRET_LENGTH_BYTES,
        scopes=SCOPES,
    )

    assert new_client.credentials_valid("this-is-not-the-right-secret") is False
    assert new_client.credentials_valid(secret) is True


def test_get_root_client_detail_no_root_client_hash():
    with pytest.raises(ValueError):
        _get_root_client_detail("test", None, SCOPES)


def test_get_root_client_detail_no_scopes(config):
    with pytest.raises(ValueError):
        _get_root_client_detail("test", config.security.OAUTH_ROOT_CLIENT_SECRET_HASH)
