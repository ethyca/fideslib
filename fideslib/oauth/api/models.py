from typing import Dict, List, Optional

from fastapi import Form, Request
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel

from fideslib.oauth.api.exceptions import InvalidAuthorizationSchemeException


class AccessToken(BaseModel):
    """
    A wrapper for the `access_token` returned upon successful authentication.
    """

    access_token: str


class ClientCreatedResponse(BaseModel):
    """
    Response model for client creation.
    """

    client_id: str
    client_secret: str

    @classmethod
    def get_field_names(cls) -> List[str]:
        """
        Return a list of all field names specified on this schema.
        """

        return list(cls.schema().get("properties", {}).keys())

    class Config:
        """
        Allow ORM access on all schemas.
        """

        orm_mode = True


class OAuth2ClientCredentialsBearer(OAuth2):
    """
    Requires a valid OAuth2 bearer token using the client credentials flow, e.g.
    "Authorization: Bearer <token>". See /oauth/token for details on how to
    authenticate and receive a valid token.

    Adapted from:
    https://github.com/tiangolo/fastapi/blob/f0388915a8b1cd9f3ae2259bace234ac6249c51a/fastapi/security/oauth2.py#L140
    """

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}

        flows = OAuthFlows(clientCredentials={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            auto_error=auto_error,
            description=description,
            flows=flows,
            scheme_name=scheme_name,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        scheme, param = get_authorization_scheme_param(
            request.headers.get(key="Authorization", default="")
        )

        if scheme.lower() != "bearer":
            if self.auto_error:
                raise InvalidAuthorizationSchemeException()

        return param


class OAuth2ClientCredentialsRequestForm:
    """
    Request model used to authenticate via OAuth2 client credentials. This uses
    application/x-www-form-urlencoded instead of JSON, to follow the OAuth2 spec:
    https://datatracker.ietf.org/doc/html/rfc6749#section-4.4.2

    Adapted from:
    https://github.com/tiangolo/fastapi/blob/f0388915a8b1cd9f3ae2259bace234ac6249c51a/fastapi/security/oauth2.py#L13
    """

    def __init__(
        self,
        grant_type: str = Form(None, regex="client_credentials"),
        scope: str = Form(""),
        client_id: Optional[str] = Form(None),
        client_secret: Optional[str] = Form(None),
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type
        self.scopes = scope.split()
