# pylint: disable=C0116

import os

import pytest

from fideslib.logging.logger import MASKED, NotPii, _mask_pii_for_logs


@pytest.fixture
def fides_log_pii_false():
    original_value = os.getenv("FIDES__LOG_PII")
    os.environ["FIDES__LOG_PII"] = "False"
    yield
    if original_value:
        os.environ["FIDES__LOG_PII"] = original_value


@pytest.fixture
def fides_log_pii_true():
    original_value = os.getenv("FIDES__LOG_PII")
    os.environ["FIDES__LOG_PII"] = "True"
    yield
    if original_value:
        os.environ["FIDES__LOG_PII"] = original_value


@pytest.fixture
def toggle_testing_envvar():
    original_value = os.getenv("TESTING")
    del os.environ["TESTING"]
    yield
    if original_value:
        os.environ["TESTING"] = original_value


@pytest.mark.usefixtures("toggle_testing_envvar")
def test_logger_masks_pii():
    some_data = "some_data"
    result = _mask_pii_for_logs(some_data)
    print(result)
    assert result == MASKED


def test_logger_does_not_mask_whitelist():
    some_data = NotPii("some_data")
    result = _mask_pii_for_logs(some_data)
    assert result == some_data
