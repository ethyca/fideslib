"""
The endpoint URL paths exposed by an OAuthRouter instance.
"""

OAUTH_PREFIX = "/oauth"

SCOPE = "/scope"

CLIENT = "/client"
CLIENT_BY_ID = CLIENT + "/{client_id}"
CLIENT_SCOPE = CLIENT_BY_ID + SCOPE

TOKEN = "/token"
