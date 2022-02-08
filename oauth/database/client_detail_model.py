import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import ARRAY, Column, DateTime, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

import cryptography as crypto
import oauth.jwt as jwt
from oauth.api.utils import generate_jwe
from oauth.scopes import SCOPES


class ClientDetail:
    """
    The persisted details about a client in the system.
    """

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return "oauth_clients"

    id = Column(String(255), primary_key=True, index=True, default=str(uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    hashed_secret = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    scopes = Column(ARRAY(String), nullable=False, default="{}")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def create_access_code_jwe(
        self,
        app_encryption_key: str,
        encoding: str = "utf-8",
    ) -> str:
        """
        Generates a JWE from the client detail provided.
        """

        payload = {
            # client id may not be necessary
            jwt.JWE_PAYLOAD_CLIENT_ID: self.id,
            jwt.JWE_PAYLOAD_SCOPES: self.scopes,
            jwt.JWE_ISSUED_AT: datetime.now().isoformat(),
        }

        return generate_jwe(json.dumps(payload), app_encryption_key, encoding)

    @classmethod
    def create_client_and_secret(
        cls,
        client_id_bytelength: int,
        client_secret_bytelength: int,
        db: Session,
        encoding: str = "utf-8",
        scopes: List[str] = None,
    ) -> Tuple["ClientDetail", str]:
        """
        Creates a ClientDetail and returns it, along with the unhashed
        secret, so it can be returned to the user.
        """

        if not scopes:
            scopes = []

        client_id = crypto.generate_secure_random_string(client_id_bytelength)
        secret = crypto.generate_secure_random_string(client_secret_bytelength)

        salt = crypto.generate_salt(encoding)
        hashed_secret = crypto.hash_with_salt(
            secret.encode(encoding),
            salt.encode(encoding),
        )

        resource = ClientDetail(
            hashed_secret=hashed_secret,
            id=client_id,
            salt=salt,
            scopes=scopes,
        )

        ClientDetail.persist(db, resource)
        return resource, secret

    def credentials_valid(self, provided_secret: str, encoding: str = "utf-8") -> bool:
        """
        Verifies that the provided secret is correct.
        """

        provided_secret_hash = crypto.hash_with_salt(
            provided_secret.encode(encoding),
            self.salt.encode(encoding),
        )

        return provided_secret_hash == self.hashed_secret

    def delete(self, db: Session) -> None:
        """
        Removes a ClientDetail from db.
        """

        db.delete(self)
        db.commit()

    @classmethod
    def get(
        cls,
        db: Session,
        *,
        client_id: Any,
        encoding: str = "utf-8",
        root_client_id: str,
        root_client_secret_hash: Tuple[str, bytes]
    ) -> Optional["ClientDetail"]:
        """
        Fetch a client record via a table ID.
        """

        if client_id == root_client_id:
            return _get_root_client_detail(
                root_client_secret_hash,
                root_client_id,
                encoding,
            )

        return db.query(cls).get(client_id)

    @classmethod
    def persist(cls, db: Session, resource: "ClientDetail") -> None:
        """
        Manually write a ClientDetail resource to db.
        """

        try:
            db.add(resource)
            db.commit()
            db.refresh(resource)
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    def update(self, db: Session, *, data: Dict[str, Any]) -> None:
        """
        Modifies a ClientDetail in-place, and persists the changes to db.
        """

        for key, val in data.items():
            setattr(self, key, val)

        ClientDetail.persist(db, self)


def _get_root_client_detail(
    root_client_secret_hash: Optional[Tuple[str, bytes]],
    root_client_id: str,
    encoding: str,
) -> Optional[ClientDetail]:
    assert root_client_secret_hash is not None
    return ClientDetail(
        hashed_secret=root_client_secret_hash[0],
        id=root_client_id,
        salt=root_client_secret_hash[1].decode(encoding),
        scopes=SCOPES,
    )
