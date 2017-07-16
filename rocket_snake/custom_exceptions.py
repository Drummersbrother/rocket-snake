"""Custom exceptions for the library."""


class NoAPIKeyError(ValueError):
    pass


class APIServerError(ConnectionError):
    pass


class APIBadResponseCodeError(ConnectionError):
    pass


class RateLimitError(APIBadResponseCodeError):
    pass
