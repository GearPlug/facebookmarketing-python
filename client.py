import exception
import requests
import hashlib
import hmac
from enumerate import MethodEnum, ErrorEnum
from urllib.parse import urlencode


class Client(object):
    BASE_URL = 'https://graph.facebook.com/'

    def __init__(self, app_id, app_secret, version):
        self.app_id = app_id
        self.app_secret = app_secret
        self.version = version
        self._access_token = None
        self.BASE_URL += self.version

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value

    def get_app_token(self):
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'grant_type': 'client_credentials'
        }
        url = self.BASE_URL + '/oauth/access_token'
        return self._request(MethodEnum.GET, url, params=params)

    def authorization_url(self, redirect_url, scope):
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_url,
            'scope': ' '.join(scope)
        }
        url = 'https://facebook.com/dialog/oauth?' + urlencode(params)
        return url

    def exchange_code(self, redirect_url, code):
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_url,
            'client_secret': self.app_secret,
            'code': code
        }
        url = self.BASE_URL + '/oauth/access_token'
        return self._request(MethodEnum.GET, url, params=params)

    def extend_token(self, token):
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': token
        }
        url = self.BASE_URL + '/oauth/access_token'
        return self._request(MethodEnum.GET, url, params=params)

    def inspect_token(self, input_token, token):
        params = {
            'input_token': input_token,
            'access_token': token
        }
        url = self.BASE_URL + '/debug_token'
        return self._request(MethodEnum.GET, url, params=params)

    def _get_params(self):
        return {
            'access_token': self._access_token,
            'appsecret_proof': self._get_app_secret_proof()
        }

    def _get_app_secret_proof(self):
        h = hmac.new(self.app_secret.encode('utf-8'), msg=self.access_token.encode('utf-8'), digestmod=hashlib.sha256)
        return h.hexdigest()

    def get_account(self):
        params = self._get_params()
        url = self.BASE_URL + '/me'
        return self._request(MethodEnum.GET, url, params=params)

    def get_pages(self):
        params = self._get_params()
        url = self.BASE_URL + '/me/accounts'
        return self._request(MethodEnum.GET, url, params=params)

    def get_leads(self, form_id, from_date=None):
        params = self._get_params()
        params['from_date'] = from_date
        url = self.BASE_URL + '/{}/leads'.format(form_id)
        return self._request(MethodEnum.GET, url=url, params=params)

    def get_forms(self, page_id):
        params = self._get_params()
        url = self.BASE_URL + '/{}/leadgen_forms'.format(page_id)
        return self._request(MethodEnum.GET, url=url, params=params)

    def _request(self, method, url, params=None, data=None):
        response = requests.request(method.value, url, params=params, data=data)
        return self._parse(response.json())

    def _parse(self, response):
        if 'error' in response:
            error = response['error']
        elif 'data' in response and 'error' in response['data']:
            error = response['data']['error']
        else:
            error = None

        if error:
            code = error['code']
            message = error['message']
            try:
                error_enum = ErrorEnum(code)
            except Exception:
                raise exception.Error('Error: {}. Message {}'.format(code, message))
            if error_enum == ErrorEnum.UnknownError:
                raise exception.UnknownError(message)
            elif error_enum == ErrorEnum.AppRateLimit:
                raise exception.AppRateLimitError(message)
            elif error_enum == ErrorEnum.AppPermissionRequired:
                raise exception.AppPermissionRequiredError(message)
            elif error_enum == ErrorEnum.UserRateLimit:
                raise exception.UserRateLimitError(message)
            elif error_enum == ErrorEnum.InvalidParameter:
                raise exception.InvalidParameterError(message)
            elif error_enum == ErrorEnum.SessionKeyInvalid:
                raise exception.SessionKeyInvalidError(message)
            elif error_enum == ErrorEnum.IncorrectPermission:
                raise exception.IncorrectPermissionError(message)
            elif error_enum == ErrorEnum.InvalidOauth20AccessToken:
                raise exception.PermissionError(message)
            elif error_enum == ErrorEnum.ExtendedPermissionRequired:
                raise exception.ExtendedPermissionRequiredError(message)
            else:
                raise exception.Error('Error: {}. Message {}'.format(code, message))

        return response
