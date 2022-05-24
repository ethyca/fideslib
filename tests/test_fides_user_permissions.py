# pylint: disable=missing-function-docstring

from unittest.mock import MagicMock

from fideslib.models.fides_user_permissions import FidesUserPermissions
from fideslib.oauth.scopes import PRIVACY_REQUEST_READ


def test_create_user_permissions():
    permissions: FidesUserPermissions = FidesUserPermissions.create(  # type: ignore
        db=MagicMock(),
        data={"user_id": "test", "scopes": [PRIVACY_REQUEST_READ]},
    )

    assert permissions.user_id == "test"
    assert permissions.scopes == [PRIVACY_REQUEST_READ]
