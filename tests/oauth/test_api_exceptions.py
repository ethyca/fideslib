from fastapi import status

import fideslib.oauth.api.exceptions as exc
from fideslib.oauth.scopes import SCOPES


def test_authentication_exception():
    exception = exc.AuthenticationException()

    # Includes a 401 status code
    assert exception.status_code == status.HTTP_401_UNAUTHORIZED

    # Includes a secure message
    assert exception.detail == "Missing or invalid credentials"


def test_authorization_exception():
    exception = exc.AuthorizationException()

    # Includes a 403 status code
    assert exception.status_code == status.HTTP_403_FORBIDDEN

    # Includes a secure message
    assert exception.detail == "Insufficient permissions to perform this action"


def test_client_write_failed_exception():
    exception = exc.ClientWriteFailedException()

    # Includes a 422 status code
    assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Includes a secure message
    assert exception.detail == "Failed to create client"


def test_client_not_found_exception():
    client_id = "test_client"
    exception = exc.ClientNotFoundException(client_id)

    # Includes a 404 status code
    assert exception.status_code == status.HTTP_404_NOT_FOUND

    # Includes the correct client_id in the response details
    assert "id" in exception.detail
    assert exception.detail["id"] == client_id


def test_expired_token_exception():
    exception = exc.ExpiredTokenException()

    # Includes a 403 status code
    assert exception.status_code == status.HTTP_403_FORBIDDEN

    # Includes a secure message
    assert exception.detail == "OAuth token expired"


def test_invalid_authorization_scheme_exception():
    exception = exc.InvalidAuthorizationSchemeException()

    # Includes a 401 status code
    assert exception.status_code == status.HTTP_401_UNAUTHORIZED

    # Includes a secure message
    assert exception.detail == "Failed to authenticate"

    # Includes the correct auth scheme in a response header
    assert "WWW-Authenticate" in exception.headers
    assert exception.headers["WWW-Authenticate"] == "Bearer"


def test_invalid_scope_exception():
    invalid_scopes = ["invalid:one", "invalid:two"]
    exception = exc.InvalidScopeException(invalid_scopes)

    # Includes a 422 status code
    assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Includes a secure message
    assert "error" in exception.detail
    assert exception.detail["error"] == "Invalid scope provided"

    # Reflects the invalid scopes
    assert "invalid_scopes" in exception.detail
    assert exception.detail["invalid_scopes"] == invalid_scopes

    # Includes a sorted reference of valid scopes
    assert "valid_scopes" in exception.detail
    SCOPES.sort()
    assert exception.detail["valid_scopes"] == SCOPES
