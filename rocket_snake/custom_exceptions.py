"""Custom exceptions for the library."""


class NoAPIKeyError(ValueError):
    pass


class APIServerError(ConnectionError):
    pass


class APINotFoundError(ConnectionError):
    pass


class APIBadResponseCodeError(ConnectionError):
    pass


class RateLimitError(APIBadResponseCodeError):
    pass

class InvalidAPIKeyError(APIBadResponseCodeError):
    pass