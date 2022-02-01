from datetime import datetime
from typing import List

from jose import jwe
from jose.constants import ALGORITHMS

from oauth.api.exceptions import InvalidScopeException
from oauth.scopes import SCOPES


def extract_payload(jwe_string: str, encryption_key: str) -> str:
    """
    Given a JWE, extracts the payload and returns it in string form.
    """

    return jwe.decrypt(jwe_string, encryption_key)


def is_token_expired(issued_at: datetime, token_duration_min: int) -> bool:
    """
    Returns True if `issued_at` is earlier than `token_duration_min` ago.
    """

    return (datetime.now() - issued_at).total_seconds() / 60.0 > token_duration_min


def generate_jwe(payload: str, encryption_key: str, encoding: str) -> str:
    """
    Generates a JWE with the provided payload. Returns a string representation.
    """

    return jwe.encrypt(
        payload,
        encryption_key,
        encryption=ALGORITHMS.A256GCM,
    ).decode(encoding)


def validate_scopes(scopes: List[str]) -> None:
    """
    Raises an InvalidScopeException if any of the provided scopes are invalid.
    """

    invalid_scopes = [scope for scope in scopes if scope not in SCOPES]
    if len(invalid_scopes) > 0:
        raise InvalidScopeException(invalid_scopes)
