from typing import List

from fastapi import HTTPException
from pydantic import validator
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from fideslib.oauth.scopes import SCOPES
from fideslib.schemas.base_class import BaseSchema


class UserPermissionsCreate(BaseSchema):
    """Data required to create a FidessUserPermissions record."""

    scopes: List[str]

    @validator("scopes")
    @classmethod
    def validate_scopes(cls, scopes: List[str]) -> List[str]:
        """Validates that all incoming scopes are valid"""
        diff = set(scopes).difference(set(SCOPES))
        if len(diff) > 0:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid Scope(s) {diff}. Scopes must be one of {SCOPES}.",
            )
        return scopes


class UserPermissionsEdit(UserPermissionsCreate):
    """Data required to edit a FidesUserPermissions record."""

    id: str


class UserPermissionsResponse(UserPermissionsCreate):
    """Response after creating, editing, or retrieving a FidesUserPermissions record."""

    id: str
    user_id: str
