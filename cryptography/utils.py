import hashlib
import secrets

from bcrypt import gensalt


def hash_with_salt(text: bytes, salt: bytes) -> str:
    """
    Hashes `text` using SHA-512, including the provided salt.
    Returns the hex string representation.
    """

    return hashlib.sha512(text + salt).hexdigest()


def generate_secure_random_string(bytelength: int) -> str:
    """
    Generates and returns a securely random string containing
    twice the number of hex digits as `bytelength`.
    """

    return secrets.token_hex(bytelength)


def generate_salt(encoding: str) -> str:
    """
    Generates a salt string. Returns a string using the
    configured encoding.
    """

    return gensalt().decode(encoding)
