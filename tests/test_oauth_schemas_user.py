# pylint: disable=missing-function-docstring

import pytest

from fideslib.cryptography.cryptographic_util import str_to_b64_str
from fideslib.oauth.schemas.user import UserCreate


@pytest.mark.parametrize(
    "password, message",
    [
        ("Short1!", "eight characters"),
        ("Nonumber*", "one number"),
        ("nocapital1!", "one capital"),
        ("NOLOWERCASE1!", "one lowercase"),
        ("Nosymbol1", "one symbol"),
    ],
)
def test_bad_password(password, message):
    with pytest.raises(ValueError) as excinfo:
        UserCreate(
            username="test",
            password=str_to_b64_str(password),
            first_name="test",
            last_name="test",
        )

    assert message in str(excinfo.value)


def test_user_create_user_name_with_spaces():
    with pytest.raises(ValueError):
        UserCreate(
            username="some user",
            password="Testtest1!",
            first_name="test",
            last_name="test",
        )
