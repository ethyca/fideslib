"""
The endpoint URL paths exposed by an OAuthRouter instance.
"""

OAUTH_PREFIX = "/oauth"

CLIENT = f"{OAUTH_PREFIX}/client"
CLIENT_BY_ID = CLIENT + "/{client_id}"
CLIENT_SCOPE = CLIENT_BY_ID + "/scope"

SCOPE = f"{OAUTH_PREFIX}/scope"
TOKEN = f"{OAUTH_PREFIX}/token"
