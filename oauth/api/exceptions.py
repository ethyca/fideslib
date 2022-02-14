from typing import List

from fastapi import HTTPException, status

from oauth.scopes import SCOPES


class AuthenticationException(HTTPException):
    """
    To be raised when attempting to fetch an access token using
    invalid credentials.
    """

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid credentials",
        )


class AuthorizationException(HTTPException):
    """
    To be raised when attempting to perform an action for which
    the token does not have the required scope assigned.
    """

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to perform this action",
        )


class ClientWriteFailedException(HTTPException):
    """
    To be raised when a client cannot be created.
    """

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to create client",
        )


class ClientNotFoundException(HTTPException):
    """
    To be raised when attempting to fetch a client that does not exist.
    """

    def __init__(self, client_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Client does not exist",
                "id": client_id,
            },
        )


class ExpiredTokenException(HTTPException):
    """
    To be raised when a provided token is expired.
    """

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OAuth token expired",
        )


class InvalidAuthorizationSchemeException(HTTPException):
    """
    To be raised when attempting to authenticate with an unexpected
    Authorization header value.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidScopeException(HTTPException):
    """
    To be raised when a provided scope does not exist.
    """

    def __init__(self, invalid_scopes: List[str]) -> None:
        SCOPES.sort()

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Invalid scope provided",
                "invalid_scopes": invalid_scopes,
                "valid_scopes": SCOPES,
            },
        )
