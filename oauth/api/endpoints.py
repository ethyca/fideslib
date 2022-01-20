OAUTH_PREFIX = "/oauth"

CLIENT = f"{OAUTH_PREFIX}/client"
CLIENT_BY_ID = CLIENT + "/{client_id}"
CLIENT_SCOPE = CLIENT + "/{client_id}/scope"

SCOPE = f"{OAUTH_PREFIX}/scope"
TOKEN = f"{OAUTH_PREFIX}/token"
