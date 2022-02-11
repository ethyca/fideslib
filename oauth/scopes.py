CREATE = "create"
DELETE = "delete"
READ = "read"
UPDATE = "update"

CLIENT = "client"
CLIENT_CREATE = f"{CLIENT}:{CREATE}"
CLIENT_DELETE = f"{CLIENT}:{DELETE}"
CLIENT_READ = f"{CLIENT}:{READ}"
CLIENT_UPDATE = f"{CLIENT}:{UPDATE}"

SCOPE_READ = f"scope:{READ}"

SCOPE_DOCS = {
    CLIENT_CREATE: "Create OAuth clients",
    CLIENT_DELETE: "Remove OAuth clients",
    CLIENT_READ: "View current scopes for OAuth clients",
    CLIENT_UPDATE: "Modify existing scopes for OAuth clients",
    SCOPE_READ: "View authorization scopes",
}

SCOPES = list(SCOPE_DOCS.keys())
