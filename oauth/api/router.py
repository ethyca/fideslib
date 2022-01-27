from logging import getLogger
from typing import List

from fastapi import APIRouter, Body, Depends, Request, Security, status
from fastapi.security import HTTPBasic
from sqlalchemy.orm import Session

import oauth.api.endpoints as endpoints
from oauth.api.exceptions import AuthenticationException, ClientNotFoundException
from oauth.api.models import (
    AccessToken,
    ClientCreatedResponse,
    OAuth2ClientCredentialsRequestForm,
)
from oauth.api.utils import validate_scopes, verify_oauth_client
from oauth.database.models import ClientDetail
from oauth.scopes import (
    CLIENT_CREATE,
    CLIENT_DELETE,
    CLIENT_READ,
    CLIENT_UPDATE,
    SCOPE_READ,
    SCOPES,
)

logger = getLogger(__name__)
router = APIRouter(prefix=endpoints.OAUTH_PREFIX, tags=["OAuth"])


@router.post(endpoints.TOKEN, response_model=AccessToken)
async def acquire_access_token(
    request: Request,
    form_data: OAuth2ClientCredentialsRequestForm = Depends(),
    db: Session = Depends(),
) -> AccessToken:
    """
    Given a set of credentials, returns an access token.
    """

    basic_credentials = await HTTPBasic(auto_error=False)(request)

    if form_data.client_id and form_data.client_secret:
        client_id = form_data.client_id
        client_secret = form_data.client_secret
    elif basic_credentials:
        client_id = basic_credentials.username
        client_secret = basic_credentials.password
    else:
        raise AuthenticationException()

    client_detail = ClientDetail.get(db, client_id=client_id)
    if client_detail is None:
        raise AuthenticationException()

    if not client_detail.credentials_valid(client_secret):
        raise AuthenticationException()

    logger.info("Creating access token for client with ID '%s'", client_id)
    return AccessToken(access_token=client_detail.create_access_code_jwe())


@router.post(
    endpoints.CLIENT,
    dependencies=[Security(verify_oauth_client, scopes=[CLIENT_CREATE])],
    response_model=ClientCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    *,
    db: Session = Depends(),
    scopes: List[str] = Body([]),
) -> ClientCreatedResponse:
    """
    Creates a new client and returns the credentials.
    """

    validate_scopes(scopes)

    client, secret = ClientDetail.create_client_and_secret(db, scopes)
    logger.info("Created new client with ID '%s'", client.id)

    return ClientCreatedResponse(client_id=client.id, client_secret=secret)


@router.delete(
    endpoints.CLIENT_BY_ID,
    dependencies=[Security(verify_oauth_client, scopes=[CLIENT_DELETE])],
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_client(client_id: str, db: Session = Depends()) -> None:
    """
    Deletes the client associated with the client_id.
    """

    client = ClientDetail.get(db, client_id=client_id)
    if client is not None:
        logger.info("Deleting client with ID '%s'", client_id)
        client.delete(db)


@router.get(
    endpoints.CLIENT_SCOPE,
    dependencies=[Security(verify_oauth_client, scopes=[CLIENT_READ])],
    response_model=List[str],
)
def get_client_scopes(client_id: str, db: Session = Depends()) -> List[str]:
    """
    Returns a list of the scopes associated with the client.
    """

    logger.info("Fetching current permissions for client with ID '%s'", client_id)
    client = ClientDetail.get(db, client_id=client_id)
    return client.scopes if client is not None else []


@router.put(
    endpoints.CLIENT_SCOPE,
    dependencies=[Security(verify_oauth_client, scopes=[CLIENT_UPDATE])],
    response_model=None,
)
def set_client_scopes(
    client_id: str,
    scopes: List[str],
    db: Session = Depends(),
) -> None:
    """
    Overwrites the client's scopes with those provided.
    """

    client = ClientDetail.get(db, client_id=client_id)
    if not client:
        raise ClientNotFoundException(client_id)

    validate_scopes(scopes)

    logger.info(
        "Updating permissions for client with ID '%s' to: [%s]",
        client_id,
        ", ".join(scopes.sort()),
    )
    client.update(db, data={"scopes": scopes})


@router.get(
    endpoints.SCOPE,
    dependencies=[Security(verify_oauth_client, scopes=[SCOPE_READ])],
    response_model=List[str],
)
def read_scopes() -> List[str]:
    """
    Returns a list of all scopes available for assignment in the system.
    """

    return SCOPES.sort()
