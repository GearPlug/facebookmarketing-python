from enum import Enum


class ErrorEnum(Enum):
    UnknownError = 1
    AppRateLimit = 4
    AppPermissionRequired = 10
    UserRateLimit = 17
    InvalidParameter = 100
    SessionKeyInvalid = 102
    IncorrectPermission = 104
    InvalidOauth20AccessToken = 190
    PermissionError = 200
    ExtendedPermissionRequired = 294
