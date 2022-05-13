import re
from datetime import datetime
from typing import Optional

from pydantic import validator

from fideslib.schemas.base_class import BaseSchema


class UserCreate(BaseSchema):
    """Data required to create a FidesopsUser"""

    username: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]

    @validator("username")
    def validate_username(cls, username: str) -> str:  # pylint: disable=E0213, R0201
        """Ensure password does not have spaces"""
        if not username:
            raise ValueError("Must enter username.")
        if " " in username:
            raise ValueError("Usernames cannot have spaces.")
        return username

    @validator("password")
    def validate_password(cls, password: str) -> str:  # pylint: disable=E0213, R0201
        """Add some password requirements"""
        if len(password) < 8:
            raise ValueError("Password must have at least eight characters.")
        if re.search("[0-9]", password) is None:
            raise ValueError("Password must have at least one number.")
        if re.search("[A-Z]", password) is None:
            raise ValueError("Password must have at least one capital letter.")
        if re.search("[a-z]", password) is None:
            raise ValueError("Password must have at least one lowercase letter.")
        if re.search(r"[\W]", password) is None:
            raise ValueError("Password must have at least one symbol.")

        return password


class UserLogin(BaseSchema):
    """Similar to UserCreate except we do not need the extra validation on
    username and password.
    """

    username: str
    password: str


class UserResponse(BaseSchema):
    """Response after requesting a User"""

    id: str
    username: str
    created_at: datetime
    first_name: Optional[str]
    last_name: Optional[str]


class UserCreateResponse(BaseSchema):
    """Response after creating a FidesopsUser"""

    id: str


class PrivacyRequestReviewer(BaseSchema):
    """Data we can expose via the PrivacyRequest.reviewer relation"""

    id: str
    username: str