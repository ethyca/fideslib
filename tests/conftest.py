# pylint: disable=missing-function-docstring

import logging
import os
from pathlib import Path

import pytest

from fideslib.core.config import get_config

logger = logging.getLogger(__name__)

ROOT_PATH = Path().absolute()


@pytest.fixture(scope="session")
def config():
    yield get_config()


@pytest.fixture(autouse=True, scope="session")
def env_vars():
    os.environ["TESTING"] = "True"


@pytest.fixture
def fides_toml_path():
    yield ROOT_PATH / "fides.toml"
