from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session

from fideslib.core.config import config
from fideslib.cryptography.cryptographic_util import (
    generate_salt,
    generate_secure_random_string,
    hash_with_salt,
)
from fideslib.cryptography.schemas.jwt import (
    JWE_ISSUED_AT,
    JWE_PAYLOAD_CLIENT_ID,
    JWE_PAYLOAD_SCOPES,
)
from fideslib.db.base_class import Base
from fideslib.models.fides_user import FidesUser
from fideslib.oauth.api.scope_registry import SCOPE_REGISTRY
from fideslib.oauth.jwt import generate_jwe

DEFAULT_SCOPES: list[str] = []


class ClientDetail(Base):  # type: ignore
    """The persisted details about a client in the system"""

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=E0213
        return "client"

    hashed_secret = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    scopes = Column(ARRAY(String), nullable=False, default="{}")
    fides_key = Column(String, index=True, unique=True, nullable=True)
    user_id = Column(
        String, ForeignKey(FidesUser.id_field_path), nullable=True, unique=True
    )

    @classmethod
    def create_client_and_secret(
        cls,
        db: Session,
        scopes: list[str] | None = None,
        fides_key: str = None,
        user_id: str = None,
    ) -> tuple["ClientDetail", str]:
        """Creates a ClientDetail and returns that along with the unhashed secret
        so it can be returned to the user on create
        """

        client_id = generate_secure_random_string(
            config.security.OAUTH_CLIENT_ID_LENGTH_BYTES
        )
        secret = generate_secure_random_string(
            config.security.OAUTH_CLIENT_SECRET_LENGTH_BYTES
        )

        if not scopes:
            scopes = DEFAULT_SCOPES

        salt = generate_salt()
        hashed_secret = hash_with_salt(
            secret.encode(config.security.ENCODING),
            salt.encode(config.security.ENCODING),
        )

        client = super().create(
            db,
            data={
                "id": client_id,
                "salt": salt,
                "hashed_secret": hashed_secret,
                "scopes": scopes,
                "fides_key": fides_key,
                "user_id": user_id,
            },
        )
        return client, secret

    @classmethod
    def get(
        cls, db: Session, *, id: Any  # pylint: disable=W0622
    ) -> ClientDetail | None:
        """Fetch a database record via a table ID"""
        if id == config.security.OAUTH_ROOT_CLIENT_ID:
            return _get_root_client_detail()
        return super().get(db, id=id)

    def create_access_code_jwe(self) -> str:
        """Generates a JWE from the client detail provided"""
        payload = {
            # client id may not be necessary
            JWE_PAYLOAD_CLIENT_ID: self.id,
            JWE_PAYLOAD_SCOPES: self.scopes,
            JWE_ISSUED_AT: datetime.now().isoformat(),
        }
        return generate_jwe(json.dumps(payload))

    def credentials_valid(self, provided_secret: str) -> bool:
        """Verifies that the provided secret is correct"""
        provided_secret_hash = hash_with_salt(
            provided_secret.encode(config.security.ENCODING),
            self.salt.encode(config.security.ENCODING),
        )

        return provided_secret_hash == self.hashed_secret


def _get_root_client_detail() -> ClientDetail | None:
    root_secret = config.security.OAUTH_ROOT_CLIENT_SECRET_HASH
    assert root_secret is not None
    return ClientDetail(
        id=config.security.OAUTH_ROOT_CLIENT_ID,
        hashed_secret=root_secret[0],
        salt=root_secret[1].decode(config.security.ENCODING),
        scopes=SCOPE_REGISTRY,
    )
