import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, Optional, Tuple, Type, Union

import bcrypt
import tomli
import validators
from pydantic import (
    BaseSettings,
    Extra,
    PostgresDsn,
    ValidationError,
    root_validator,
    validator,
)
from pydantic.env_settings import SettingsSourceCallable

from fideslib.exceptions import MissingConfig

logger = logging.getLogger(__name__)


class FidesSettings(BaseSettings):
    """Class used as a base model for configuration subsections."""

    class Config:
        # Need to allow extras because the inheriting class will have more info
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Set environment variables to take precedence over init values."""
            return env_settings, init_settings, file_secret_settings


class DatabaseSettings(FidesSettings):
    """Configuration settings for Postgres."""

    SERVER: str
    USER: str
    PASSWORD: str
    DB: str = "test"
    PORT: str = "5432"
    TEST_DB: str = "test"

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    SQLALCHEMY_TEST_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, str]) -> str:
        """Join DB connection credentials into a connection string"""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values["USER"],
            password=values["PASSWORD"],
            host=values["SERVER"],
            port=values.get("PORT"),
            path=f"/{values.get('DB') or ''}",
        )

    @validator("SQLALCHEMY_TEST_DATABASE_URI", pre=True)
    @classmethod
    def assemble_test_db_connection(
        cls, v: Optional[str], values: Dict[str, str]
    ) -> str:
        """Join DB connection credentials into a connection string"""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values["USER"],
            password=values["PASSWORD"],
            host=values["SERVER"],
            port=values["PORT"],
            path=f"/{values.get('TEST_DB') or ''}",
        )

    class Config:
        env_prefix = "FIDES__DATABASE__"


class SecuritySettings(FidesSettings):
    """Configuration settings for Security variables."""

    AES_ENCRYPTION_KEY_LENGTH: int = 16
    AES_GCM_NONCE_LENGTH: int = 12
    APP_ENCRYPTION_KEY: str
    DRP_JWT_SECRET: str

    @validator("APP_ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key_length(
        cls, v: Optional[str], values: Dict[str, str]
    ) -> Optional[str]:
        """Validate the encryption key is exactly 32 characters"""
        if v is None or len(v.encode(values.get("ENCODING", "UTF-8"))) != 32:
            raise ValueError(
                "APP_ENCRYPTION_KEY value must be exactly 32 characters long"
            )
        return v

    CORS_ORIGINS: List[str] = []

    @validator("CORS_ORIGINS", pre=True)
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Return a list of valid origins for CORS requests"""

        def validate(values: List[str]) -> None:
            for value in values:
                if value != "*":
                    if not validators.url(value):
                        raise ValueError(f"{value} is not a valid url")

        if isinstance(v, str) and not v.startswith("["):
            values = [i.strip() for i in v.split(",")]
            validate(values)

            return values
        if isinstance(v, (list, str)):
            validate(v)  # type: ignore

            return v
        raise ValueError(v)

    ENCODING: str = "UTF-8"

    # OAuth
    OAUTH_ROOT_CLIENT_ID: str
    OAUTH_ROOT_CLIENT_SECRET: str
    OAUTH_ROOT_CLIENT_SECRET_HASH: Optional[Tuple]
    OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    OAUTH_CLIENT_ID_LENGTH_BYTES = 16
    OAUTH_CLIENT_SECRET_LENGTH_BYTES = 16

    @root_validator(pre=True)
    @classmethod
    def assemble_root_access_token(cls, values: Dict[str, str]) -> Dict[str, str]:
        """Sets a hashed value of the root access key.

        This is hashed as it is not wise to return a plaintext for of the
        root credential anywhere in the system.
        """
        value = values.get("OAUTH_ROOT_CLIENT_SECRET")
        if not value:
            raise MissingConfig(
                "OAUTH_ROOT_CLIENT_SECRET is required", SecuritySettings
            )

        encoding = values.get("ENCODING", "UTF-8")

        salt = bcrypt.gensalt()
        hashed_client_id = hashlib.sha512(value.encode(encoding) + salt).hexdigest()
        values["OAUTH_ROOT_CLIENT_SECRET_HASH"] = (hashed_client_id, salt)  # type: ignore
        return values

    class Config:
        env_prefix = "FIDES__SECURITY__"


class FidesConfig(FidesSettings):
    """Configuration variables for the FastAPI project."""

    database: DatabaseSettings
    security: SecuritySettings

    is_test_mode: bool = os.getenv("TESTING", "").lower() == "true"
    hot_reloading: bool = os.getenv("FIDES__HOT_RELOAD", "").lower() == "true"
    dev_mode: bool = os.getenv("FIDES__DEV_MODE", "").lower() == "true"

    class Config:
        case_sensitive = True


def load_file(file_names: Union[List[Path], List[str]]) -> str:
    """Load a file from the first matching location.

    In order, will check:
    - A path set at ENV variable FIDES__CONFIG_PATH
    - The current directory
    - The parent directory
    - Two directories up for the current directory
    - The parent_directory/.fides
    - users home (~) directory
    raises FileNotFound if none is found
    """

    possible_directories = [
        os.getenv("FIDES__CONFIG_PATH"),
        os.curdir,
        os.pardir,
        os.path.abspath(os.path.join(os.curdir, "..", "..")),
        os.path.join(os.pardir, ".fides"),
        os.path.expanduser("~"),
    ]

    directories = [d for d in possible_directories if d]

    for dir_str in directories:
        for file_name in file_names:
            possible_location = os.path.join(dir_str, file_name)
            if possible_location and os.path.isfile(possible_location):
                logger.info("Loading file %s from %s", file_name, dir_str)
                return possible_location

    raise FileNotFoundError


def load_toml(file_names: Union[List[Path], List[str]]) -> MutableMapping[str, Any]:
    """Load toml file from possible locations specified in load_file.

    Will raise FileNotFoundError or ValidationError on missing or
    bad file
    """
    file_name = load_file(file_names)
    with open(file_name, "rb") as f:
        return tomli.load(f)


def get_config(
    class_name: Type[FidesConfig] = FidesConfig,
    *,
    file_names: Union[List[Path], List[str]] = [
        "fidesops.toml",
        "fidesctl.toml",
        "fides.toml",
    ],
) -> FidesConfig:
    """
    Attempt to read config file named fidesops.toml, fidesctl.toml, or fides.toml from:
    - env var FIDES__CONFIG_PATH
    - local directory
    - parent directory
    - home directory
    This will fail on the first encountered bad conf file.
    """
    try:
        return class_name.parse_obj(load_toml(file_names))
    except (FileNotFoundError) as e:
        if isinstance(file_names, list):
            if len(file_names) == 1:
                logger.warning("%s could not be loaded: %s", file_names[0], e)
            else:
                logger.warning(
                    "%s could not be loaded: %s",
                    " or ".join([str(x) for x in file_names]),
                    e,
                )
        else:
            logger.warning("%s could not be loaded: %s", file_names, e)
        # If no path is specified Pydantic will attempt to read settings from
        # the environment. Default values will still be used if the matching
        # environment variable is not set.
        try:
            return class_name()
        except ValidationError as exc:
            logger.error("ValidationError: %s", exc)
            # If FidesConfig is missing any required values Pydantic will throw
            # an ImportError. This means the config has not been correctly specified
            # so we can throw the missing config error.
            raise MissingConfig(exc.args[0]) from exc
