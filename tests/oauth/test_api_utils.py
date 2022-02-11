# pylint: disable=missing-function-docstring

from datetime import datetime, timedelta

import pytest

import oauth.api.utils as utils
from oauth.api.exceptions import InvalidScopeException
from oauth.scopes import SCOPES


def test_is_token_expired():
    token_duration = 5

    # Returns True if `issued_at` is prior to `now` - `token_duration_min`
    six_minutes_ago = datetime.now() - timedelta(minutes=6)
    assert utils.is_token_expired(six_minutes_ago, token_duration)

    # Returns True if `issued_at` is equal to `now` - `token_duration_min`
    five_minutes_ago = datetime.now() - timedelta(minutes=5)
    assert utils.is_token_expired(five_minutes_ago, token_duration)

    # Returns False if `issued_at` is after `now` - `token_duration_min`
    four_minutes_ago = datetime.now() - timedelta(minutes=4)
    assert not utils.is_token_expired(four_minutes_ago, token_duration)


def test_validate_scopes():
    # Succeeds when only valid scopes are provided
    assert utils.validate_scopes(SCOPES[0:3]) is None

    # Raises an InvalidScopeException when invalid scopes are provided
    with pytest.raises(InvalidScopeException):
        utils.validate_scopes(
            SCOPES[0:2] + ["invalid:one", "invalid:two", "invalid:three"]
        )
