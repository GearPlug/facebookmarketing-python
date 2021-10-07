import hashlib
import hmac
from urllib.parse import urlencode, urlparse

import requests

from facebookmarketing import exceptions
from facebookmarketing.decorators import access_token_required
from facebookmarketing.enumerators import ErrorEnum


class Client(object):
    BASE_URL = 'https://graph.facebook.com/'

    def __init__(self, app_id, app_secret, version='v12.0', requests_hooks=None):
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

    @access_token_required
    def get_account(self):
        """Gets the authed account information.

        Returns:
            A dict.

        """
        params = self._get_params()
        return self._get('/me', params=params)

    @access_token_required
    def get_pages(self):
        """Gets tge authed account pages.

        Returns:
            A dict.

        """
        params = self._get_params()

        new_result = self._get('/me/accounts', params=params)
        del params['access_token']  # Las urls siguiente ya incluyen el access token, pero no el proof.
        page_list = new_result['data']
        while 'paging' in new_result and 'next' in new_result['paging']:
            # La URL de next incluye el base, lo cambiamos a ''.
            new_result = self._get(new_result['paging']['next'].replace(self.BASE_URL, ''), params=params)
            page_list += new_result['data']
        return {'data': page_list}  # Se retorna un dict con el key data para mantener compatibilidad.

    @access_token_required
    def get_page_token(self, page_id):
        """Gets page token for the given page.

        Args:
            page_id: String with Page's ID.

        Returns:
            dict
        """
        pages = self.get_pages()
        page = next((p for p in pages['data'] if p['id'] == str(page_id)), None)
        if not page:
            return None
        return page['access_token']

    def get_page_subscribed_apps(self, page_id, token):
        """

        Args:
            page_id:
            token:

        Returns:

        """
        params = self._get_params(token)
        return self._get('/{}/subscribed_apps'.format(page_id), params=params)

    def create_page_subscribed_apps(self, page_id, token, params=None):
        """

        Args:
            page_id:
            token:
            params:

        Returns:

        """
        _params = self._get_params(token)
        if params and isinstance(params, dict):
            _params.update(params)
        return self._post('/{}/subscribed_apps'.format(page_id), params=_params)

    def delete_page_subscribed_apps(self, page_id, token):
        """

        Args:
            page_id:
            token:

        Returns:

        """
        params = self._get_params(token)
        return self._delete('/{}/subscribed_apps'.format(page_id), params=params)

    def get_app_subscriptions(self, application_token):
        """

        Args:
            token:

        Returns:

        """
        params = self._get_params(application_token)
        return self._get('/{}/subscriptions'.format(self.app_id), params=params)

    def create_app_subscriptions(self, object, callback_url, fields, verify_token, token):
        """

        Args:
            object:
            callback_url:
            fields:
            verify_token:
            token:

        Returns:

        """
        o = urlparse(callback_url)

        if o.scheme != 'https':
            raise exceptions.HttpsRequired

        params = self._get_params(token)
        params.update({
            'object': object,
            'callback_url': callback_url,
            'fields': fields,
            'verify_token': verify_token
        })
        return self._post('/{}/subscriptions'.format(self.app_id), params=params)

    def delete_app_subscriptions(self, token):
        """

        Args:
            token:

        Returns:

        """
        params = self._get_params(token)
        return self._delete('/{}/subscriptions'.format(self.app_id), params=params)

    @access_token_required
    def get_ad_account_leadgen_forms(self, page_id, page_access_token=None):
        """Gets the forms for the given page.

        Args:
            page_id: A string with Page's ID.

        Returns:
            A dict.

        """
        params = self._get_params(token=page_access_token)
        new_result = self._get('/{}/leadgen_forms'.format(page_id), params=params)
        del params['access_token']  # Las urls siguiente ya incluyen el access token, pero no el proof.
        form_list = new_result['data']
        while 'paging' in new_result and 'next' in new_result['paging']:
            # La URL de next incluye el base, lo cambiamos a ''.
            new_result = self._get(new_result['paging']['next'].replace(self.BASE_URL, ''), params=params)
            form_list += new_result['data']
        return {'data': form_list}

    @access_token_required
    def get_leadgen(self, leadgen_id):
        """
            Get a single leadgen given an id.

        Args:
            leadgen_id: A string with the leadgen's ID.

        Returns:
            A dict.
        """
        params = self._get_params()
        return self._get('/{0}'.format(leadgen_id), params=params)

    @access_token_required
    def get_ad_leads(self, leadgen_form_id, from_date=None, to_date=None, after=None):
        """Gets the leads for the given form.

        Args:
            leadgen_form_id: A string with the Form's ID.
            from_date: A timestamp.
            to_date: A timestamp.
            after: A cursor.

        Returns:
            A dict.

        """
        params = self._get_params()
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
        if after:
            params['after'] = after
        return self._get('/{}/leads'.format(leadgen_form_id), params=params)

    def get_custom_audience(self, account_id, fields=None):
        """

        Args:
            account_id:
            fields:

        Returns:

        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._get('/{}/customaudiences'.format(account_id), params=params)

    def get_adaccounts_id(self, fields=None):
        """

        Returns:

        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._get('/me/adaccounts', params=params)

    def get_instagram(self, page_id, fields=None):
        """

        Returns:

        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._get('/{}'.format(page_id), params=params)

    def get_instagram_media(self, page_id, fields=None):
        """

        Returns:

        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._get('/{}/media'.format(page_id), params=params)

    def get_instagram_media_object(self, media_id, fields=None):
        """

        Returns:

        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._get('/{}'.format(media_id), params=params)

    def get_instagram_media_comment(self, media_id):
        """

        Returns:

        """
        params = self._get_params()
        return self._get('/{}/comments'.format(media_id), params=params)

    def get_instagram_hashtag(self, page_id, fields=None):
        """

        Returns:

        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._get('/{}/media'.format(page_id), params=params)

    def get_instagram_hashtag_search(self, user_id, query):
        """

        Returns:

        """
        params = self._get_params()
        params['user_id'] = user_id
        params['q'] = query
        return self._get('/ig_hashtag_search', params=params)

    def get_instagram_hashtag_object(self, hashtag_id, fields=None):
        """

        Returns:

        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._get('/{}'.format(hashtag_id), params=params)

    def get_instagram_hashtag_recent_media(self, hashtag_id, user_id, fields=None):
        """

        Returns:

        """
        params = self._get_params()
        params['user_id'] = user_id
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._get('/{}/recent_media'.format(hashtag_id), params=params)

    def get_instagram_hashtag_top_media(self, hashtag_id, user_id, fields=None):
        """

        Returns:

        """
        params = self._get_params()
        params['user_id'] = user_id
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._get('/{}/top_media'.format(hashtag_id), params=params)

    def _get(self, endpoint, **kwargs):
        return self._request('GET', endpoint, **kwargs)

    def _post(self, endpoint, **kwargs):
        return self._request('POST', endpoint, **kwargs)

    def _delete(self, endpoint, **kwargs):
        return self._request('DELETE', endpoint, **kwargs)

    def _request(self, method, endpoint, headers=None, **kwargs):
        _headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if headers:
            _headers.update(headers)
        if self.requests_hooks:
            kwargs.update({'hooks': self.requests_hooks})
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
