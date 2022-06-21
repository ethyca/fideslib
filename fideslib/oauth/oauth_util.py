from __future__ import annotations

import json
from datetime import datetime

from fastapi.security import SecurityScopes
from jose import jwe
from sqlalchemy.orm import Session

from fideslib.core.config import FidesConfig
from fideslib.cryptography.schemas.jwt import (
    JWE_ISSUED_AT,
    JWE_PAYLOAD_CLIENT_ID,
    JWE_PAYLOAD_SCOPES,
)
from fideslib.exceptions import AuthorizationError
from fideslib.models.client import ClientDetail


def extract_payload(jwe_string: str, encryption_key: str) -> str:
    """Given a jwe, extracts the payload and returns it in string form."""
    return jwe.decrypt(jwe_string, encryption_key)


def is_token_expired(issued_at: datetime | None, token_duration_min: int) -> bool:
    """Returns True if the datetime is earlier than token_duration_min ago."""
    if not issued_at:
        return True

    return (datetime.now() - issued_at).total_seconds() / 60.0 > token_duration_min


def verify_oauth_client(
    security_scopes: SecurityScopes,
    authorization: str,
    *,
    db: Session,
    config: FidesConfig,
) -> ClientDetail:
    """Verifies that the access token provided in the authorization header contains
    the necessary scopes specified by the caller.

    Raises a 403 forbidden error if not.
    """
    token_data = json.loads(
        extract_payload(authorization, config.security.APP_ENCRYPTION_KEY)
    )

    issued_at = token_data.get(JWE_ISSUED_AT, None)
    if not issued_at:
        raise AuthorizationError(detail="Not Authorized for this action")

    if is_token_expired(
        datetime.fromisoformat(issued_at),
        config.security.OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES,
    ):
        raise AuthorizationError(detail="Not Authorized for this action")

    assigned_scopes = token_data[JWE_PAYLOAD_SCOPES]
    if not set(security_scopes.scopes).issubset(set(assigned_scopes)):
        raise AuthorizationError(detail="Not Authorized for this action")

    client_id = token_data.get(JWE_PAYLOAD_CLIENT_ID)
    if not client_id:
        raise AuthorizationError(detail="Not Authorized for this action")

    client = ClientDetail.get(
        db, object_id=client_id, config=config, scopes=security_scopes.scopes
    )
    if not client:
        raise AuthorizationError(detail="Not Authorized for this action")

    if not set(assigned_scopes).issubset(set(client.scopes)):
        # If the scopes on the token are not a subset of the scopes available
        # to the associated oauth client, this token is not valid
        raise AuthorizationError(detail="Not Authorized for this action")
    return client
