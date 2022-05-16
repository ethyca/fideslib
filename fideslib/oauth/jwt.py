from jose import jwe
from jose.constants import ALGORITHMS

from fideslib.core.config import config

_JWT_ENCRYPTION_ALGORITHM = ALGORITHMS.A256GCM


def generate_jwe(payload: str) -> str:
    """Generates a JWE with the provided payload.

    Returns a string representation.
    """
    return jwe.encrypt(
        payload,
        config.security.APP_ENCRYPTION_KEY,
        encryption=_JWT_ENCRYPTION_ALGORITHM,
    ).decode(config.security.ENCODING)
