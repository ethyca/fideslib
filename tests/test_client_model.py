# pylint: disable=missing-function-docstring

from unittest.mock import MagicMock

from fideslib.cryptography.cryptographic_util import hash_with_salt
from fideslib.models.client import ClientDetail


def test_create_client_and_secret(config):
    new_client, secret = ClientDetail.create_client_and_secret(
        MagicMock(),
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


def test_credentials_valid(config):
    new_client, secret = ClientDetail.create_client_and_secret(
        MagicMock(),
        config.security.OAUTH_CLIENT_ID_LENGTH_BYTES,
        config.security.OAUTH_CLIENT_SECRET_LENGTH_BYTES,
    )

    assert new_client.credentials_valid("this-is-not-the-right-secret") is False
    assert new_client.credentials_valid(secret) is True
