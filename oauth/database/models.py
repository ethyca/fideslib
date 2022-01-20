import json
from datetime import datetime
from typing import Any, List, Optional, Tuple

from sqlalchemy import ARRAY, Column, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session

import cryptography.utils as crypto
import oauth.jwt as jwt
from oauth.api.utils import generate_jwe
from oauth.scopes import SCOPES

# FIXME: Base is not defined, was previously imported from fidesops.db.base_class
class ClientDetail(Base):
    """
    The persisted details about a client in the system.
    """

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return "client"

    hashed_secret = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    scopes = Column(ARRAY(String), nullable=False, default="{}")

    @classmethod
    def create_client_and_secret(
        cls,
        db: Session,
        scopes: List[str] = None,
    ) -> Tuple["ClientDetail", str]:
        """
        Creates a ClientDetail and returns it, along with the unhashed
        secret, so it can be returned to the user.
        """

        if not scopes:
            scopes = []

        # FIXME: Requires the OAUTH_CLIENT_ID_LENGTH_BYTES argument
        client_id = crypto.generate_secure_random_string()
        # FIXME: Requires the OAUTH_CLIENT_SECRET_LENGTH_BYTES argument
        secret = crypto.generate_secure_random_string()

        # FIXME: Requires the security.ENCODING argument
        salt = crypto.generate_salt()
        hashed_secret = crypto.hash_with_salt(
            # FIXME: Both of the below require the security.ENCODING argument
            secret.encode(),
            salt.encode(),
        )

        client = super().create(
            db,
            data={
                "hashed_secret": hashed_secret,
                "id": client_id,
                "salt": salt,
                "scopes": scopes,
            },
        )

        return client, secret

    @classmethod
    def get(cls, db: Session, *, client_id: Any) -> Optional["ClientDetail"]:
        """
        Fetch a client record via a table ID.
        """

        # FIXME: Should be compared to OAUTH_ROOT_CLIENT_ID
        if client_id == "":
            # FIXME: Requires the OAUTH_ROOT_CLIENT_SECRET_HASH argument
            return _get_root_client_detail()

        return super().get(db, id=client_id)

    def create_access_code_jwe(self) -> str:
        """
        Generates a JWE from the client detail provided.
        """

        payload = {
            # client id may not be necessary
            jwt.JWE_PAYLOAD_CLIENT_ID: self.id,
            jwt.JWE_PAYLOAD_SCOPES: self.scopes,
            jwt.JWE_ISSUED_AT: datetime.now().isoformat(),
        }

        # FIXME: Requires the security.APP_ENCRYPTION_KEY argument
        return generate_jwe(json.dumps(payload))

    def credentials_valid(self, provided_secret: str) -> bool:
        """
        Verifies that the provided secret is correct.
        """

        provided_secret_hash = crypto.hash_with_salt(
            # FIXME: Both of the below calls to .encode() require the security.ENCODING argument
            provided_secret.encode(),
            self.salt.encode(),
        )

        return provided_secret_hash == self.hashed_secret


def _get_root_client_detail(
    root_client_secret_hash: Optional[Tuple],
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
