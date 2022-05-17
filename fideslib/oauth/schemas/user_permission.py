from typing import List

from fastapi import HTTPException
from pydantic import validator
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from fideslib.oauth.api.scope_registry import SCOPE_REGISTRY
from fideslib.schemas.base_class import BaseSchema


class UserPermissionsCreate(BaseSchema):
    """Data required to create a FidessUserPermissions record."""

    scopes: List[str]

    @validator("scopes")
    def validate_scopes(  # pylint: disable=E0213, R0201
        cls, scopes: List[str]
    ) -> List[str]:
        """Validates that all incoming scopes are valid"""
        diff = set(scopes).difference(set(SCOPE_REGISTRY))
        if len(diff) > 0:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid Scope(s) {diff}. Scopes must be one of {SCOPE_REGISTRY}.",
            )
        return scopes


class UserPermissionsEdit(UserPermissionsCreate):
    """Data required to edit a FidesUserPermissions record."""

    id: str


class UserPermissionsResponse(UserPermissionsCreate):
    """Response after creating, editing, or retrieving a FidesUserPermissions record."""

    id: str
    user_id: str
