import hashlib
import secrets
from base64 import b64decode, b64encode

import bcrypt


def hash_with_salt(text: bytes, salt: bytes) -> str:
    """Hashes the text using SHA-512 with the provided salt and returns the hex string
    representation"""
    return hashlib.sha512(text + salt).hexdigest()


def generate_secure_random_string(length: int) -> str:
    """Generates a securely random string using Python secrets library
    that is twice the length of the specified input"""
    return secrets.token_hex(length)


def generate_salt(encoding: str = "UTF-8") -> str:
    """Generates a salt using bcrypt and returns a string using the configured
    default encoding
    """
    return bcrypt.gensalt().decode(encoding)


def bytes_to_b64_str(bytestring: bytes, encoding: str = "UTF-8") -> str:
    """Converts random bytes into a utf-8 encoded string"""
    return b64encode(bytestring).decode(encoding)


def b64_str_to_bytes(encoded_str: str, encoding: str = "UTF-8") -> bytes:
    """Converts encoded string into bytes"""
    return b64decode(encoded_str.encode(encoding))


def b64_str_to_str(encoded_str: str, encoding: str = "UTF-8") -> str:
    """Converts encoded string into str"""
    return b64decode(encoded_str).decode(encoding)


def str_to_b64_str(string: str, encoding: str = "UTF-8") -> str:
    """Converts str into a utf-8 encoded string"""
    return b64encode(string.encode(encoding)).decode(encoding)
