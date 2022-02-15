from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

import fideslib.oauth.api.endpoints as endpoints
from fideslib.oauth.api.router import OAuthRouter


def get_dummy_db():
    db = sessionmaker()()
    try:
        yield db
    finally:
        db.close()


oauth_router = OAuthRouter(
    "encryption_key",
    get_dummy_db,
    "root_client_id",
    ("root_client_hash", b"salt"),
)


def test_oauth_router_init():
    # Sets the default tag when none are provided
    assert oauth_router.tags == ["OAuth"]

    # Adds all routes
    assert len(oauth_router.routes) == 6


app = FastAPI(title="test_app")
app.include_router(oauth_router)
client = TestClient(app)


def test_acquire_access_token():
    # When no credentials are provided, responds with a 401
    response = client.post(endpoints.OAUTH_PREFIX + endpoints.TOKEN)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Missing or invalid credentials"}


def test_create_client():
    # When no credentials are provided, responds with a 401
    response = client.post(endpoints.OAUTH_PREFIX + endpoints.CLIENT)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Failed to authenticate"}
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_delete_client():
    # When no credentials are provided, responds with a 401
    response = client.delete(endpoints.OAUTH_PREFIX + endpoints.CLIENT_BY_ID)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Failed to authenticate"}
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_get_client_scopes():
    # When no credentials are provided, responds with a 401
    response = client.get(endpoints.OAUTH_PREFIX + endpoints.CLIENT_SCOPE)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Failed to authenticate"}
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_set_client_scopes():
    # When no credentials are provided, responds with a 401
    response = client.put(endpoints.OAUTH_PREFIX + endpoints.CLIENT_SCOPE)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Failed to authenticate"}
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_read_scopes():
    # When no credentials are provided, responds with a 401
    response = client.get(endpoints.OAUTH_PREFIX + endpoints.SCOPE)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Failed to authenticate"}
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"
