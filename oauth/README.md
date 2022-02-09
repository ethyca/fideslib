# OAuth

This package exposes a [FastAPI](https://fastapi.tiangolo.com/) `APIRouter`, called `OAuthRouter`. It is intended to provide support for OAuth client management.

## Requirements

The `OAuthRouter` assumes that the importing FastAPI app implements a PostgreSQL database that includes an `oauth_clients` table with the following columns:

#### `oauth_clients`

| Column Name     | Type     | Notes |
|-----------------|----------|-------|
| `id`            | String   | Primary key, indexed |
| `created_at`    | Datetime | Timezone included |
| `hashed_secret` | String   | Non-nullable |
| `salt`          | String   | Non-nullable |
| `scopes`        | []String | Non-nullable, defaults to an empty array |
| `updated_at`    | Datetime | Timezone included |

## Usage

1. Include `fideslib[oauth]` as a project dependency

    ```txt title="<code>requirements.txt</code>"
    fideslib[oauth]==1.0.0
    ```

2. Include an `OAuthRouter` instance in your FastAPI app:

    ```python
    from fastapi import FastAPI
    from fideslib.oauth.api.router import OAuthRouter

    app = FastAPI(title="my_app")
    app.include_router(OAuthRouter(...))    # Configure as desired
    ```

## Configuration

An `OAuthRouter` instance can be configured with several options:

| Option                           | Type                      | Required?                          | Description |
|----------------------------------|---------------------------|------------------------------------|-------------|
| `app_encryption_key`             | String                    | Yes                                | AES256 encryption key used for database record encryption and JSON web encryption (JWE) payloads. Must be exactly 32 bytes (256 bits). |
| `db`                             | Generator                 | Yes                                | A Python Generator that returns a SQLAlchemy `sessionmaker`, corresponding to database sessions for the importing FastAPI app. |
| `oauth_root_client_id`           | String                    | Yes                                | A unique ID, used for the "root" OAuth client. |
| `oauth_root_client_secret_hash`  | Tuple[String, Bytestring] | Yes                                | The client secret used for the "root" OAuth client, and associated salt string. |
| `encoding`                       | String                    | No (default: `"UTF-8"`)            | The string encoding type, with which all bytestrings will be encoded/decoded. |
| `oauth_access_token_expire_min`  | Integer                   | No (default: `11520` (eight days)) | The number of minutes for which OAuth access tokens should be valid. |
| `oauth_client_id_bytelength`     | Integer                   | No (default: `16`)                 | The bytelength of OAuth client IDs. |
| `oauth_client_secret_bytelength` | Integer                   | No (default:`16`)                  | The bytelength of OAuth client secrets. |
| `prefix`                         | String                    | No (default: `"/oauth"`)           | A URL path section that should precede all endpoints added by the `OAuthRouter`. |
| `tags`                           | List[String]              | No (default: `["OAuth"]`)          | A list of FastAPI tags applied to the `OAuthRouter`. |

### Example

```python
from fideslib.oauth.api.router import OAuthRouter
from my_app.database import get_db

oauth_router = OAuthRouter(
  app_encryption_key="foobar",
  db=get_db,
  oauth_root_client_id="root_client_id",
  oauth_root_client_secret_hash=(
    "root_client_secret",
    b'$2b$12$vOQuva2LZmkPOWAcxeuBZ.',
  ),

  # Optional; the values included below are the defaults

  encoding="utf-8",
  oauth_access_token_expire_min=11520,   # Eight days
  oauth_client_id_bytelength=16,
  oauth_client_secret_bytelength=16,
  prefix="/oauth",
  tags=["OAuth"],
)
```
