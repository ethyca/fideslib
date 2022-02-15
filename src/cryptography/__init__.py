from base64 import b64encode, b64decode
from hashlib import sha512
from secrets import token_hex

from bcrypt import gensalt


def bytes_to_b64_str(bytestring: bytes, encoding: str = "UTF-8") -> str:
    """
    Converts `bytestring` into a string literal, encoded with the specified encoding.
    """

    return b64encode(bytestring).decode(encoding)


def b64_str_to_bytes(encoded: str, encoding: str = "UTF-8") -> bytes:
    """
    Converts `encoded` into a bytestring using the specified encoding.
    """

    return b64decode(encoded.encode(encoding))


def hash_with_salt(text: bytes, salt: bytes) -> str:
    """
    Hashes `text` using SHA-512, including the provided `salt`.
    Returns the hex string representation.
    """

    return sha512(text + salt).hexdigest()


def generate_secure_random_string(bytelength: int) -> str:
    """
    Generates and returns a securely random string containing
    twice the number of hex digits as `bytelength`.
    """

    return token_hex(bytelength)


def generate_salt(encoding: str = "UTF-8") -> str:
    """
    Generates a salt string. Returns a string using the configured encoding.
    """

    return gensalt().decode(encoding)
