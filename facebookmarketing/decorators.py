from facebookmarketing.exceptions import AccessTokenRequired
from functools import wraps


def access_token_required(func):
    @wraps(func)
    def helper(*args, **kwargs):
        instance = args[0]
        if not instance._client.access_token:
            raise AccessTokenRequired('You must set the Access Token.')
        return func(*args, **kwargs)

    return helper
