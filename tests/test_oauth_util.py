# pylint: disable=missing-function-docstring

import json

from fideslib.oauth.jwt import generate_jwe
from fideslib.oauth.oauth_util import extract_payload


def test_jwe_create_and_extract() -> None:
    payload = {"hello": "hi there"}
    encryption_key = "d9a74e98829dbf57c4ca36e1788a48d2"
    jwt_string = generate_jwe(json.dumps(payload), encryption_key)
    payload_from_svc = json.loads(extract_payload(jwt_string, encryption_key))
    assert payload_from_svc["hello"] == payload["hello"]
