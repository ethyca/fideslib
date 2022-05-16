# pylint: disable=C0116

import logging
import os
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)

ROOT_PATH = Path().absolute()


@pytest.fixture(autouse=True, scope="session")
def env_vars():
    os.environ["TESTING"] = "True"


@pytest.fixture
def fides_toml_path():
    yield ROOT_PATH / "fides.toml"
