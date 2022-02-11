"""
The endpoint URL paths exposed by an OAuthRouter instance.
"""

OAUTH_PREFIX = "/oauth"

CLIENT = "/client"
CLIENT_BY_ID = CLIENT + "/{client_id}"
CLIENT_SCOPE = CLIENT_BY_ID + "/scope"

SCOPE = "/scope"
TOKEN = "/token"
