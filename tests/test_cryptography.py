# pylint: disable=line-too-long,missing-function-docstring

import pytest

from fideslib import cryptography as crypto

TEST_BYTESTRING = b"foobar"
B64_ENCODED = "Zm9vYmFy"


def test_bytes_to_b64_str():
    # Converts a given bytestring to it's b64 encoded counterpart.
    assert crypto.bytes_to_b64_str(TEST_BYTESTRING) == B64_ENCODED

    # Errors with an invalid encoding
    with pytest.raises(LookupError):
        _ = crypto.bytes_to_b64_str(TEST_BYTESTRING, "foobar")


def test_b64_str_to_bytes():
    # Converts a given b64 encoded string to it's bytestring counterpart.
    assert crypto.b64_str_to_bytes(B64_ENCODED) == TEST_BYTESTRING

    # Errors with an invalid encoding
    with pytest.raises(LookupError):
        _ = crypto.b64_str_to_bytes(B64_ENCODED, "foobar")


def test_hash_with_salt():
    # Returns the hex representation of the SHA-512 hash of the given bytestring + salt.
    assert (
        crypto.hash_with_salt(TEST_BYTESTRING, b"wow-thats-salty")
        == "28ee0dd3e82232b61ffd91915feff38366d3d9f5040b09c47ec4793df7690c5291b1d0259846336d641dea72f7c1cfa2017362b80e157d1ecf0bdce6de154a7e"
    )


def test_generate_secure_random_string():
    bytelength = 26

    # Generates a random string with a hex length twice that of the given bytelength.
    assert len(crypto.generate_secure_random_string(bytelength)) == 2 * bytelength

    # Generates unique strings
    generated = set()
    for _ in range(10):
        generated.add(crypto.generate_secure_random_string(bytelength))

    assert len(generated) == 10


def test_generate_salt():
    # Generates unique salt strings
    generated = set()
    for _ in range(10):
        generated.add(crypto.generate_salt())

    assert len(generated) == 10

    # Errors with an invalid encoding
    with pytest.raises(LookupError):
        _ = crypto.generate_salt("foobar")
