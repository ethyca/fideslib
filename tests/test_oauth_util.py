# pylint: disable=missing-function-docstring, redefined-outer-name

import json
from datetime import datetime

import pytest

from fideslib.oauth.jwt import generate_jwe
from fideslib.oauth.oauth_util import extract_payload, is_token_expired


@pytest.fixture
def encryption_key():
    yield "d9a74e98829dbf57c4ca36e1788a48d2"


def test_jwe_create_and_extract(encryption_key) -> None:
    payload = {"hello": "hi there"}
    jwe_string = generate_jwe(json.dumps(payload), encryption_key)
    payload_from_svc = json.loads(extract_payload(jwe_string, encryption_key))
    assert payload_from_svc["hello"] == payload["hello"]


@pytest.mark.parametrize(
    "issued_at, token_duration_min, expected",
    [
        (datetime(2020, 1, 1), 1, True),
        (datetime.now(), 60, False),
        (None, 60, True),
    ],
)
def test_is_token_expired(issued_at, token_duration_min, expected):
    assert is_token_expired(issued_at, token_duration_min) is expected
