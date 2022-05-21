# pylint: disable=C0116

import pytest
from fastapi import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from fideslib.oauth.schemas.user import UserCreate
from fideslib.oauth.schemas.user_permission import UserPermissionsCreate
from fideslib.oauth.scopes import USER_DELETE, USER_PERMISSION_CREATE


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
            username="test", password=password, first_name="test", last_name="test"
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


def test_user_permission_catch_invalid_scopes():
    invalid_scopes = ["not a real scope", "invalid scope here"]
    with pytest.raises(HTTPException) as exc:
        UserPermissionsCreate(scopes=invalid_scopes)

    assert exc.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert invalid_scopes[0] in exc.value.detail
    assert invalid_scopes[1] in exc.value.detail


def test_user_permission_scope_validation():
    valid_scopes = [USER_DELETE, USER_PERMISSION_CREATE]
    permissions = UserPermissionsCreate(scopes=valid_scopes)
    assert permissions.scopes == valid_scopes
