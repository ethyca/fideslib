import hashlib
import logging
import os
from typing import Any, Dict, List, MutableMapping, Optional, Tuple, Type, Union

import bcrypt
import tomli
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, ValidationError, validator
from pydantic.env_settings import SettingsSourceCallable

from fideslib.exceptions import MissingConfig
from fideslib.utils.logger import NotPii

logger = logging.getLogger(__name__)


class FidesSettings(BaseSettings):
    """Class used as a base model for configuration subsections."""

    class Config:  # pylint: disable=C0115
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,  # pylint: disable=W0613
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Set environment variables to take precedence over init values."""
            return env_settings, init_settings


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
    def assemble_db_connection(  # pylint: disable=E0213, R0201
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
            port=values.get("PORT"),
            path=f"/{values.get('DB') or ''}",
        )

    @validator("SQLALCHEMY_TEST_DATABASE_URI", pre=True)
    def assemble_test_db_connection(  # pylint: disable=E0213, R0201
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

    class Config:  # pylint: disable=C0115
        env_prefix = "FIDES__DATABASE__"


class SecuritySettings(FidesSettings):
    """Configuration settings for Security variables."""

    AES_ENCRYPTION_KEY_LENGTH: int = 16
    AES_GCM_NONCE_LENGTH: int = 12
    APP_ENCRYPTION_KEY: str

    @validator("APP_ENCRYPTION_KEY")
    def validate_encryption_key_length(  # pylint: disable=E0213, R0201
        cls, v: Optional[str], values: Dict[str, str]
    ) -> Optional[str]:
        """Validate the encryption key is exactly 32 bytes"""
        if v is None or len(v.encode(values.get("ENCODING", "UTF-8"))) != 32:
            raise ValueError("APP_ENCRYPTION_KEY value must be exactly 32 bytes long")
        return v

    CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(  # pylint: disable=E0213, R0201
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """Return a list of valid origins for CORS requests"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, (list, str)):
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

    @validator("OAUTH_ROOT_CLIENT_SECRET_HASH", pre=True)
    def assemble_root_access_token(  # pylint: disable=E0213, R0201
        cls, _: Optional[str], values: Dict[str, str]
    ) -> Tuple:
        """Returns a hashed value of the root access key.

        This is hashed as it is not wise to return a plaintext for of the
        root credential anywhere in the system.
        """
        value = values["OAUTH_ROOT_CLIENT_SECRET"]
        if not value:
            raise MissingConfig(
                "OAUTH_ROOT_CLIENT_SECRET is required", DatabaseSettings
            )

        encoding = values["ENCODING"]
        if not encoding:
            raise MissingConfig("ENCODING is required")

        salt = bcrypt.gensalt()
        hashed_client_id = hashlib.sha512(value.encode(encoding) + salt).hexdigest()
        return hashed_client_id, salt

    class Config:  # pylint: disable=C0115
        env_prefix = "FIDES__SECURITY__"


class FidesConfig(FidesSettings):
    """Configuration variables for the FastAPI project."""

    database: DatabaseSettings
    security: SecuritySettings

    is_test_mode: bool = os.getenv("TESTING") == "True"
    hot_reloading: bool = os.getenv("FIDES__HOT_RELOAD") == "True"
    dev_mode: bool = os.getenv("FIDES__DEV_MODE") == "True"

    class Config:  # pylint: disable=C0115
        case_sensitive = True

    logger.warning(
        "Startup configuration: reloading = %s, dev_mode = %s", hot_reloading, dev_mode
    )
    logger.warning(
        'Startup configuration: pii logging = %s == "True"}',
        os.getenv("FIDES__LOG_PII"),
    )


def load_file(file_names: Union[List[str], str]) -> str:
    """Load a file and from the first matching location.

    In order, will check:
    - A path set at ENV variable FIDES__CONFIG_PATH
    - The current directory
    - The parent directory
    - users home (~) directory
    raises FileNotFound if none is found
    """

    def process_file(dir_str: str, file_name: str) -> Optional[str]:
        possible_location = os.path.join(dir_str, file_name)
        if possible_location and os.path.isfile(possible_location):
            logger.info("Loading file %s from %s", NotPii(file_name), NotPii(dir_str))
            return possible_location
        logger.debug("%s not found at %s", NotPii(file_name), NotPii(dir_str))

        return None

    possible_directories = [
        os.getenv("FIDES__CONFIG_PATH"),
        os.curdir,
        os.pardir,
        os.path.expanduser("~"),
    ]

    directories: List[str] = [d for d in possible_directories if d]

    for dir_str in directories:
        if isinstance(file_names, list):
            for file_name in file_names:
                possible_location = process_file(dir_str, file_name)
                if possible_location:
                    return possible_location
        else:
            possible_location = process_file(dir_str, file_names)
            if possible_location:
                return possible_location

    raise FileNotFoundError


def load_toml(file_names: Union[List[str], str]) -> MutableMapping[str, Any]:
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
    file_names: Union[List[str], str] = ["fides.toml", "fidesops.toml"],
) -> FidesConfig:
    """
    Attempt to read config file named fides.toml or fidesops.toml from:
    - env var FIDES__CONFIG_PATH
    - local directory
    - parent directory
    - home directory
    This will fail on the first encountered bad conf file.
    """

    try:
        return class_name.parse_obj(load_toml(file_names))
    except (FileNotFoundError, ValidationError) as e:
        if len(file_names) == 1:
            logger.warning("%s could not be loaded: %s", file_names[0], NotPii(e))
        else:
            logger.warning(
                "%s could not be loaded: %s", " or ".join(file_names), NotPii(e)
            )
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


config = get_config()
