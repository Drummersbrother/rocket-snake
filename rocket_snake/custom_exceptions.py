"""Custom exceptions for the library."""


class NoAPIKeyException(ValueError):
    pass


class APIServerError(ConnectionError):
    pass
