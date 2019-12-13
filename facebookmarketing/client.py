import hashlib
import hmac
from urllib.parse import urlencode

import requests

from facebookmarketing import exceptions
from facebookmarketing.application import Application
from facebookmarketing.comment import Comment
from facebookmarketing.enumerators import ErrorEnum
from facebookmarketing.insights import Insights
from facebookmarketing.instagram import Instagram
from facebookmarketing.marketing import Marketing
from facebookmarketing.page import Page
from facebookmarketing.post import Post
from facebookmarketing.user import User


class Client(object):
    BASE_URL = 'https://graph.facebook.com/'

    def __init__(self, app_id, app_secret, version='v5.0', requests_hooks=None):
        self.application = Application(self)
        self.comment = Comment(self)
        self.insights = Insights(self)
        self.instagram = Instagram(self)
        self.marketing = Marketing(self)
        self.page = Page(self)
        self.post = Post(self)
        self.user = User(self)

        self.app_id = app_id
        self.app_secret = app_secret
        if not version.startswith('v'):
            version = 'v' + version
        self.version = version
        self.access_token = None
        self.BASE_URL += self.version
        if requests_hooks and not isinstance(requests_hooks, dict):
            raise Exception(
                'requests_hooks must be a dict. e.g. {"response": func}. http://docs.python-requests.org/en/master/user/advanced/#event-hooks')
        self.requests_hooks = requests_hooks

    def set_access_token(self, token):
        """Sets the Access Token for its use in this library.

        Args:
            token: A string with the Access Token.

        """
        self.access_token = token

    def get_app_token(self):
        """Generates an Application Token.


        Returns:
            A dict.

        """
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'grant_type': 'client_credentials'
        }
        return self._get('/oauth/access_token', params=params)

    def authorization_url(self, redirect_uri, state, scope=None):
        """Generates an Authorization URL.

        Args:
            redirect_uri: A string with the redirect_url set in the app config.
            state:
            scope: A sequence of strings with the scopes.

        Returns:
            A string.

        """
        if scope is None:
            scope = []
        if not isinstance(scope, list):
            raise Exception('scope argument must be a list')

        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'state': state,
            'scope': ' '.join(scope),
            'response_type': 'code'
        }
        url = 'https://facebook.com/{}/dialog/oauth?'.format(self.version) + urlencode(params)
        return url

    def exchange_code(self, redirect_uri, code):
        """Exchanges a code for a Token.

        Args:
            redirect_uri: A string with the redirect_url set in the app config.
            code: A string containing the code to exchange.

        Returns:
            A dict.

        """
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'client_secret': self.app_secret,
            'code': code
        }
        return self._get('/oauth/access_token', params=params)

    def extend_token(self, token):
        """Extends a short-lived Token for a long-lived Token.

        Args:
            token: A string with the token to extend.

        Returns:
            A dict.

        """
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': token
        }
        return self._get('/oauth/access_token', params=params)

    def inspect_token(self, input_token, token):
        """Inspects an Access Token.

        Args:
            input_token: A string with the Access Token to inspect.
            token: A string with the Developer Token (App Owner) or an Application Token.

        Returns:
            A dict.

        """
        params = {
            'input_token': input_token,
            'access_token': token
        }
        return self._get('/debug_token', params=params)

    def _get_params(self, token=None):
        _token = token if token else self.access_token
        return {
            'access_token': _token,
            'appsecret_proof': self._get_app_secret_proof(_token)
        }

    def _get_app_secret_proof(self, token):
        key = self.app_secret.encode('utf-8')
        msg = token.encode('utf-8')
        h = hmac.new(key, msg=msg, digestmod=hashlib.sha256)
        return h.hexdigest()

    def _get(self, endpoint, **kwargs):
        return self._request('GET', endpoint, **kwargs)

    def _post(self, endpoint, **kwargs):
        return self._request('POST', endpoint, **kwargs)

    def _delete(self, endpoint, **kwargs):
        return self._request('DELETE', endpoint, **kwargs)

    def _request(self, method, endpoint, headers=None, parse_response=True, **kwargs):
        _headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if headers:
            _headers.update(headers)
        if self.requests_hooks:
            kwargs.update({'hooks': self.requests_hooks})
        if not parse_response:
            return requests.request(method, self.BASE_URL + endpoint, headers=_headers, **kwargs)
        return self._parse(requests.request(method, self.BASE_URL + endpoint, headers=_headers, **kwargs))

    def _parse(self, response):
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            return response.text

        if 'error' in r:
            error = r['error']
        elif 'data' in r and 'error' in r['data']:
            error = r['data']['error']
        else:
            error = None

        if error:
            code = error['code']
            message = error['message']
            try:
                error_enum = ErrorEnum(code)
            except Exception:
                raise exceptions.UnexpectedError('Error: {}. Message {}'.format(code, message))
            if error_enum == ErrorEnum.UnknownError:
                raise exceptions.UnknownError(message)
            elif error_enum == ErrorEnum.AppRateLimit:
                raise exceptions.AppRateLimitError(message)
            elif error_enum == ErrorEnum.AppPermissionRequired:
                raise exceptions.AppPermissionRequiredError(message)
            elif error_enum == ErrorEnum.UserRateLimit:
                raise exceptions.UserRateLimitError(message)
            elif error_enum == ErrorEnum.InvalidParameter:
                raise exceptions.InvalidParameterError(message)
            elif error_enum == ErrorEnum.SessionKeyInvalid:
                raise exceptions.SessionKeyInvalidError(message)
            elif error_enum == ErrorEnum.IncorrectPermission:
                raise exceptions.IncorrectPermissionError(message)
            elif error_enum == ErrorEnum.InvalidOauth20AccessToken:
                raise exceptions.PermissionError(message)
            elif error_enum == ErrorEnum.ExtendedPermissionRequired:
                raise exceptions.ExtendedPermissionRequiredError(message)
            else:
                raise exceptions.BaseError('Error: {}. Message {}'.format(code, message))
        return r
