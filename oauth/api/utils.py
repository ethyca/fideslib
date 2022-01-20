from datetime import datetime
from json import loads as load

from fastapi import Security
from fastapi.security import SecurityScopes
from jose import jwe
from jose.constants import ALGORITHMS
from sqlalchemy.orm import Session

from oauth.api.endpoints import TOKEN
from oauth.api.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ExpiredTokenException,
)
from oauth.api.models import OAuth2ClientCredentialsBearer
from oauth.database.models import ClientDetail
import oauth.jwt as jwt
from oauth.scopes import SCOPE_DOCS

oauth2_scheme = OAuth2ClientCredentialsBearer(tokenUrl=TOKEN, scopes=SCOPE_DOCS)


async def verify_oauth_client(
    security_scopes: SecurityScopes,
    db: Session,
    authorization: str = Security(oauth2_scheme),
) -> ClientDetail:
    """
    Verifies that the access token provided in the authorization header
    contains the necessary scopes specified by the caller, and responds
    with a 403 if not.
    """

    if authorization is None:
        raise AuthenticationException()

    # FIXME: extract_payload requires the security.APP_ENCRYPTION_KEY argument
    token_data = load(extract_payload(authorization))

    issued_at = token_data.get(jwt.JWE_ISSUED_AT, None)
    if not issued_at:
        raise AuthorizationException()

    # FIXME: Requires the OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES argument
    if is_token_expired(datetime.fromisoformat(issued_at)):
        raise ExpiredTokenException()

    assigned_scopes = token_data[jwt.JWE_PAYLOAD_SCOPES]
    if not set(security_scopes.scopes).issubset(assigned_scopes):
        raise AuthorizationException()

    client_id = token_data.get(jwt.JWE_PAYLOAD_CLIENT_ID)
    if not client_id:
        raise AuthorizationException()

    client = ClientDetail.get(db, client_id=client_id)
    if not client:
        raise AuthorizationException()

    if not set(assigned_scopes).issubset(set(client.scopes)):
        # If the scopes on the token are not a subset of the scopes available
        # to the associated oauth client, this token is not valid
        raise AuthorizationException()

    return client


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
