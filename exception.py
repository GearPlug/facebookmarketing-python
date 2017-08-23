class Error(Exception):
    pass


class UnknownError(Exception):
    pass


class AppRateLimitError(Exception):
    pass


class AppPermissionRequiredError(Exception):
    pass


class UserRateLimitError(Exception):
    pass


class InvalidParameterError(Exception):
    pass


class SessionKeyInvalidError(Exception):
    pass


class IncorrectPermissionError(Exception):
    pass


class InvalidOauth20AccessTokenError(Exception):
    pass


class PermissionError(Exception):
    pass


class ExtendedPermissionRequiredError(Exception):
    pass
