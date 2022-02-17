# Cryptography

This package exports cryptographic helper functions that combine operations, improve naming, and simplify the importing codebase.

## Usage

1. Include `fideslib[cryptography]` as a project dependency

    ```txt title="<code>requirements.txt</code>"
    fideslib[cryptography]==1.0.0
    ```

1. Import and use any of the exported functions:

    ```python
    import fideslib.cryptography as crypto

    ENCODING = "utf-8"

    secret = crypto.generate_secure_random_string(16)
    salt = crypto.generate_salt(ENCODING)

    hashed = crypto.hash_with_salt(
      secret.encode(ENCODING),
      salt.encode(ENCODING),
    )
    ```
