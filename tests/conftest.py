# pylint: disable=C0116

from pathlib import Path

import pytest

ROOT_PATH = Path().absolute()


@pytest.fixture
def fides_toml_path():
    yield ROOT_PATH / "fides.toml"
