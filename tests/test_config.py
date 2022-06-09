# pylint: disable=missing-function-docstring, redefined-outer-name

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from fideslib.core.config import (
    DatabaseSettings,
    SecuritySettings,
    get_config,
    load_toml,
)
from fideslib.exceptions import MissingConfig


def test_config_app_encryption_key_validation() -> None:
    app_encryption_key = "atestencryptionkeythatisvalidlen"
    with patch.dict(
        os.environ,
        {
            "FIDES__SECURITY__APP_ENCRYPTION_KEY": app_encryption_key,
        },
        clear=True,
    ):
        config = get_config()
        assert config.security.APP_ENCRYPTION_KEY == app_encryption_key


@pytest.mark.parametrize(
    "app_encryption_key",
    ["tooshortkey", "muchmuchmuchmuchmuchmuchmuchmuchtoolongkey"],
)
def test_config_app_encryption_key_validation_error(app_encryption_key) -> None:
    with patch.dict(
        os.environ,
        {
            "FIDES__SECURITY__APP_ENCRYPTION_KEY": app_encryption_key,
        },
        clear=True,
    ):
        with pytest.raises(ValidationError) as exc:
            get_config()

        assert "must be exactly 32 characters" in str(exc.value)


@pytest.fixture
def config_dict(fides_toml_path):
    yield load_toml([fides_toml_path])


def test_database_settings_sqlalchemy_database_uri_str(config_dict):
    expected = "postgresql://someuri:216f4b49bea5da4f84f05288258471852c3e325cd336821097e1e65ff92b528a@db:5432/test"
    config_dict["database"]["SQLALCHEMY_DATABASE_URI"] = expected
    settings = DatabaseSettings.parse_obj(config_dict["database"])

    assert settings.SQLALCHEMY_DATABASE_URI == expected


def test_database_settings_sqlalchemy_test_database_uri_str(config_dict):
    expected = "postgresql://someuri:216f4b49bea5da4f84f05288258471852c3e325cd336821097e1e65ff92b528a@db:5432/test"
    config_dict["database"]["SQLALCHEMY_TEST_DATABASE_URI"] = expected
    settings = DatabaseSettings.parse_obj(config_dict["database"])

    assert settings.SQLALCHEMY_TEST_DATABASE_URI == expected


@pytest.mark.parametrize(
    "file_names", ["bad.toml", ["bad.toml"], ["bad.toml", "file.toml"]]
)
def test_get_config_bad_files(file_names, caplog):
    with pytest.raises(MissingConfig):
        get_config(file_names=file_names)

    assert "could not be loaded" in caplog.text


def test_missing_config_file():
    with pytest.raises(MissingConfig):
        get_config(file_names=["bad.toml"])


def test_security_cors_str(config_dict):
    expected = "http://localhost.com"
    config_dict["security"]["CORS_ORIGINS"] = expected
    settings = SecuritySettings.parse_obj(config_dict["security"])

    assert settings.CORS_ORIGINS[0] == expected


def test_security_invalid_cors(config_dict):
    config_dict["security"]["CORS_ORIGINS"] = 1

    with pytest.raises(ValueError):
        SecuritySettings.parse_obj(config_dict["security"])


def test_security_invalid_app_encryption_key(config_dict):
    config_dict["security"]["APP_ENCRYPTION_KEY"] = "a"

    with pytest.raises(ValueError):
        SecuritySettings.parse_obj(config_dict["security"])


def test_security_missing_oauth_root_client_secret(config_dict):
    del config_dict["security"]["OAUTH_ROOT_CLIENT_SECRET"]

    with pytest.raises(MissingConfig):
        SecuritySettings.parse_obj(config_dict["security"])
