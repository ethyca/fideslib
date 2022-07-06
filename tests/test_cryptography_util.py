# pylint: disable=missing-function-docstring, redefined-outer-name

import pytest

from fideslib.cryptography.cryptographic_util import (
    b64_str_to_bytes,
    b64_str_to_str,
    bytes_to_b64_str,
    generate_salt,
    generate_secure_random_string,
    hash_with_salt,
    str_to_b64_str,
)


@pytest.fixture
def byte_string():
    yield b"foobar"


@pytest.fixture
def b64_encoded():
    yield "Zm9vYmFy"


def test_b64_str_to_bytes(b64_encoded, byte_string):
    assert b64_str_to_bytes(b64_encoded) == byte_string


def test_b64_str_to_str() -> None:
    b64_string = "aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbQ=="
    result = b64_str_to_str(b64_string)
    assert "https://www.google.com" == result


def test_bytes_to_b64_str(byte_string, b64_encoded):
    assert bytes_to_b64_str(byte_string) == b64_encoded


def test_bytes_to_b64_str_invalid_encoding():
    with pytest.raises(TypeError):
        bytes_to_b64_str("foobar")  # type: ignore


def test_generate_salt():
    # Generates unique salt strings
    generated = set()
    for _ in range(10):
        generated.add(generate_salt())

    assert len(generated) == 10


def test_generate_secure_random_string():
    bytelength = 26

    # Generates a random string with a hex length twice that of the given bytelength.
    assert len(generate_secure_random_string(bytelength)) == 2 * bytelength

    # Generates unique strings
    generated = set()
    for _ in range(10):
        generated.add(generate_secure_random_string(bytelength))

    assert len(generated) == 10


def test_hash_with_salt(encoding: str = "UTF-8") -> None:
    plain_text = "This is Plaintext. Not hashed. or salted. or chopped. or grilled."
    salt = "adobo"

    expected_hash = "3318b888645e6599289be9bee8ac0af2e63eb095213b7269f84845303abde55c7c0f9879cd69d7f453716e439ba38dd8d9b7f0bec67fe9258fb55d90e94c972d"  # pylint: disable=C0301
    hashed = hash_with_salt(
        plain_text.encode(encoding),
        salt.encode(encoding),
    )

    assert hashed == expected_hash


def test_str_to_b64_str() -> None:
    orig_string = "https://www.google.com"
    b64_string = "aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbQ=="
    result = str_to_b64_str(orig_string)
    assert b64_string == result
