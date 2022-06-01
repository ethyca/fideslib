# pylint: disable=missing-function-docstring, redefined-outer-name

from copy import deepcopy

import pytest

from fideslib.db.session import get_db_session
from fideslib.exceptions import MissingConfig


@pytest.fixture
def config_no_database_uri(config):
    new_config = deepcopy(config)
    new_config.database.SQLALCHEMY_DATABASE_URI = None
    yield new_config


def test_get_db_session_no_database_uri(config_no_database_uri):
    with pytest.raises(MissingConfig):
        get_db_session(config_no_database_uri)
