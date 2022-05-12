class KeyOrNameAlreadyExists(Exception):
    """A resource already exists with this key or name."""


class KeyValidationError(Exception):
    """The resource you're trying to create has a key specified but not
    a name specified.
    """


class MissingConfig(Exception):
    """Custom exception for when no valid configuration file is provided."""
