# pylint: disable=unused-argument

from datetime import datetime
from json import loads as load
from logging import getLogger
from typing import Any, Callable, Coroutine, Generator, List, Optional, Tuple

from fastapi import APIRouter, Body, Depends, Request, Security, status
from fastapi.security import HTTPBasic, SecurityScopes
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import oauth.api.endpoints as endpoints
import oauth.jwt as jwt
from oauth.api.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ClientWriteFailedException,
    ClientNotFoundException,
    ExpiredTokenException,
)
from oauth.api.models import (
    AccessToken,
    ClientCreatedResponse,
    OAuth2ClientCredentialsRequestForm,
)
from oauth.api.utils import (
    extract_payload,
    is_token_expired,
    oauth2_scheme,
    validate_scopes,
)
from oauth.database.client_detail_model import ClientDetail
from oauth.scopes import (
    CLIENT_CREATE,
    CLIENT_DELETE,
    CLIENT_READ,
    CLIENT_UPDATE,
    SCOPE_READ,
    SCOPES,
)

EIGHT_DAYS = 60 * 24 * 8  # Expressed in minutes


logger = getLogger(__name__)


class OAuthRouter(APIRouter):
    """
    A FastAPI `APIRouter` that includes all endpoints necessary to
    implement a complete OAuth scheme.
    """

    def __init__(
        self,
        app_encryption_key: str,
        db: Callable[[], Generator[Session, None, None]],
        oauth_root_client_id: str,
        oauth_root_client_secret_hash: Tuple[str, bytes],
        *,
        encoding: str = "utf-8",
        oauth_access_token_expire_min: int = EIGHT_DAYS,
        oauth_client_id_bytelength: int = 16,
        oauth_client_secret_bytelength: int = 16,
        prefix: str = endpoints.OAUTH_PREFIX,
        tags: Optional[List[str]] = None,
    ) -> None:
        if tags is None:
            tags = ["OAuth"]

        self.access_token_expire_min = oauth_access_token_expire_min
        self.client_id_bytelength = oauth_client_id_bytelength
        self.client_secret_bytelength = oauth_client_secret_bytelength
        self.db_func = db
        self.encoding = encoding
        self.encryption_key = app_encryption_key
        self.root_client_id = oauth_root_client_id
        self.root_client_secret_hash = oauth_root_client_secret_hash

        super().__init__(prefix=prefix, tags=tags)

        self.add_api_route(
            endpoints.TOKEN,
            self._acquire_access_token(),
            methods=["POST"],
            response_model=AccessToken,
            summary="Retrieve an access token",
        )

        self.add_api_route(
            endpoints.CLIENT,
            self._create_client(),
            dependencies=[
                Security(self._verify_oauth_client(), scopes=[CLIENT_CREATE]),
            ],
            methods=["POST"],
            response_model=ClientCreatedResponse,
            status_code=status.HTTP_201_CREATED,
            summary="Create a new client",
        )

        self.add_api_route(
            endpoints.CLIENT_BY_ID,
            self._delete_client(),
            dependencies=[
                Security(self._verify_oauth_client(), scopes=[CLIENT_DELETE]),
            ],
            methods=["DELETE"],
            response_model=None,  # Explicitly defined, to prevent overwriting
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete a client",
        )

        self.add_api_route(
            endpoints.CLIENT_SCOPE,
            self._get_client_scopes(),
            dependencies=[Security(self._verify_oauth_client(), scopes=[CLIENT_READ])],
            methods=["GET"],
            response_model=List[str],
            summary="Retrieve the current scopes for a client",
        )

        self.add_api_route(
            endpoints.CLIENT_SCOPE,
            self._set_client_scopes(),
            dependencies=[
                Security(self._verify_oauth_client(), scopes=[CLIENT_UPDATE]),
            ],
            methods=["PUT"],
            summary="Overwrite the scopes for an existing client",
        )

        self.add_api_route(
            endpoints.SCOPE,
            self.read_scopes,
            dependencies=[Security(self._verify_oauth_client(), scopes=[SCOPE_READ])],
            methods=["GET"],
            response_model=List[str],
            summary="Retrieve all available scopes",
        )

    def _acquire_access_token(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[..., Coroutine[Any, Any, AccessToken]]:
        """
        Given a set of credentials, returns an access token.
        """

        async def acquire_access_token(
            request: Request,
            *,
            db: Session = Depends(self.db_func),
            form_data: OAuth2ClientCredentialsRequestForm = Depends(),
        ) -> AccessToken:
            basic_credentials = await HTTPBasic(auto_error=False)(request)

            if form_data.client_id and form_data.client_secret:
                client_id = form_data.client_id
                client_secret = form_data.client_secret
            elif basic_credentials:
                client_id = basic_credentials.username
                client_secret = basic_credentials.password
            else:
                raise AuthenticationException()

            client_detail = ClientDetail.get(
                db,
                client_id=client_id,
                encoding=self.encoding,
                root_client_id=self.root_client_id,
                root_client_secret_hash=self.root_client_secret_hash,
            )
            if client_detail is None:
                raise AuthenticationException()

            if not client_detail.credentials_valid(client_secret, self.encoding):
                raise AuthenticationException()

            logger.info("Creating access token for client with ID '%s'", client_id)
            return AccessToken(
                access_token=client_detail.create_access_code_jwe(
                    self.encryption_key,
                    self.encoding,
                )
            )

        return acquire_access_token

    def _create_client(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[..., ClientCreatedResponse]:
        """
        Creates a new client and returns the credentials.
        """

        def create_client(
            *,
            db: Session = Depends(self.db_func),
            scopes: List[str] = Body([]),
        ) -> ClientCreatedResponse:
            validate_scopes(scopes)

            try:
                client, secret = ClientDetail.create_client_and_secret(
                    self.client_id_bytelength,
                    self.client_secret_bytelength,
                    db,
                    self.encoding,
                    scopes,
                )
                logger.info("Created new client with ID '%s'", client.id)
            except SQLAlchemyError as e:
                logger.error("Failed to create client", exc_info=True, stack_info=True)
                raise ClientWriteFailedException() from e

            return ClientCreatedResponse(client_id=client.id, client_secret=secret)

        return create_client

    def _delete_client(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[..., None]:
        """
        Deletes the client associated with the client_id.
        """

        def delete_client(
            *,
            client_id: str,
            db: Session = Depends(self.db_func),
        ) -> None:
            client = ClientDetail.get(
                db,
                client_id=client_id,
                encoding=self.encoding,
                root_client_id=self.root_client_id,
                root_client_secret_hash=self.root_client_secret_hash,
            )
            if client is not None:
                logger.info("Deleting client with ID '%s'", client_id)
                client.delete(db)

        return delete_client

    def _get_client_scopes(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[..., List[str]]:
        """
        Returns the list of scopes associated with a client.
        """

        def get_client_scopes(
            *,
            client_id: str,
            db: Session = Depends(self.db_func),
        ) -> List[str]:
            logger.info(
                "Fetching current permissions for client with ID '%s'", client_id
            )
            client = ClientDetail.get(
                db,
                client_id=client_id,
                encoding=self.encoding,
                root_client_id=self.root_client_id,
                root_client_secret_hash=self.root_client_secret_hash,
            )
            return client.scopes if client is not None else []

        return get_client_scopes

    @staticmethod
    def read_scopes(*args: Any, **kwargs: Any) -> List[str]:
        """
        Returns a list of all scopes available for assignment.
        """

        SCOPES.sort()
        return SCOPES

    def _set_client_scopes(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[..., None]:
        """
        Overwrites the client's scopes with those provided.
        """

        def set_client_scopes(
            *,
            client_id: str,
            scopes: List[str],
            db: Session = Depends(self.db_func),
        ) -> None:
            client = ClientDetail.get(
                db,
                client_id=client_id,
                encoding=self.encoding,
                root_client_id=self.root_client_id,
                root_client_secret_hash=self.root_client_secret_hash,
            )
            if not client:
                raise ClientNotFoundException(client_id)

            validate_scopes(scopes)

            try:
                client.update(db, data={"scopes": scopes})
                scopes.sort()
                logger.info(
                    "Updated permissions for client with ID '%s' to: [%s]",
                    client_id,
                    ", ".join(scopes),
                )
            except SQLAlchemyError as e:
                logger.error(
                    "Failed to update client permissions",
                    exc_info=True,
                    stack_info=True,
                )
                raise ClientWriteFailedException() from e

        return set_client_scopes

    def _verify_oauth_client(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[..., Coroutine[Any, Any, ClientDetail]]:
        """
        Verifies that the access token provided in the authorization header
        contains the necessary scopes specified by the caller.
        """

        async def verify_oauth_client(
            *,
            authorization: str = Security(oauth2_scheme),
            db: Session = Depends(self.db_func),
            security_scopes: SecurityScopes,
        ) -> ClientDetail:

            if authorization is None:
                raise AuthenticationException()

            token_data = load(extract_payload(authorization, self.encryption_key))

            issued_at = token_data.get(jwt.JWE_ISSUED_AT, None)
            if not issued_at:
                raise AuthorizationException()

            if is_token_expired(
                datetime.fromisoformat(issued_at),
                self.access_token_expire_min,
            ):
                raise ExpiredTokenException()

            assigned_scopes = token_data[jwt.JWE_PAYLOAD_SCOPES]
            if not set(security_scopes.scopes).issubset(assigned_scopes):
                raise AuthorizationException()

            client_id = token_data.get(jwt.JWE_PAYLOAD_CLIENT_ID)
            if not client_id:
                raise AuthorizationException()

            client = ClientDetail.get(
                db,
                client_id=client_id,
                encoding=self.encoding,
                root_client_id=self.root_client_id,
                root_client_secret_hash=self.root_client_secret_hash,
            )
            if not client:
                raise AuthorizationException()

            if not set(assigned_scopes).issubset(set(client.scopes)):
                # If the scopes on the token are not a subset of the scopes available
                # to the associated oauth client, this token is not valid
                raise AuthorizationException()

            return client

        return verify_oauth_client
