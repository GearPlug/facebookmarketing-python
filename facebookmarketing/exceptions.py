class BaseError(Exception):
    pass


class AccessTokenRequired(BaseError):
    pass


class HttpsRequired(BaseError):
    pass


class UnknownError(BaseError):
    pass


class UnexpectedError(BaseError):
    pass


class AppRateLimitError(BaseError):
    pass


class AppPermissionRequiredError(BaseError):
    pass


class UserRateLimitError(BaseError):
    pass


class InvalidParameterError(BaseError):
    pass


class SessionKeyInvalidError(BaseError):
    pass


class IncorrectPermissionError(BaseError):
    pass


class InvalidOauth20AccessTokenError(BaseError):
    pass


class PermissionError(BaseError):
    pass


class ExtendedPermissionRequiredError(BaseError):
    pass
