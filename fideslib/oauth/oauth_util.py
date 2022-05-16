from __future__ import annotations

from datetime import datetime

from jose import jwe

from fideslib.core.config import config


def extract_payload(jwe_string: str) -> str:
    """Given a jwe, extracts the payload and returns it in string form"""
    return jwe.decrypt(jwe_string, config.security.APP_ENCRYPTION_KEY)


def is_token_expired(issued_at: datetime | None) -> bool:
    """Returns True if the datetime is earlier than
    OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES ago"""
    if not issued_at:
        return True

    return (
        datetime.now() - issued_at
    ).total_seconds() / 60.0 > config.security.OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES
