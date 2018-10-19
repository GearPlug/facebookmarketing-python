import hashlib
import hmac

import requests
from urllib.parse import urlencode, urlparse

from facebookmarketing import exceptions
from facebookmarketing.decorators import access_token_required
from facebookmarketing.enumerators import ErrorEnum


class Client(object):
    BASE_URL = 'https://graph.facebook.com/'

    def __init__(self, app_id, app_secret, version='v2.10'):
        self.app_id = app_id
        self.app_secret = app_secret
        if not version.startswith('v'):
            version = 'v' + version
        self.version = version
        self.access_token = None
        self.BASE_URL += self.version

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

    def authorization_url(self, redirect_url, scope):
        """Generates an Authorization URL.

        Args:
            redirect_url: A string with the redirect_url set in the app config.
            scope: A sequence of strings with the scopes.

        Returns:
            A string.

        """
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_url,
            'scope': ' '.join(scope)
        }
        url = 'https://facebook.com/dialog/oauth?' + urlencode(params)
        return url

    def exchange_code(self, redirect_url, code):
        """Exchanges a code for a Token.

        Args:
            redirect_url: A string with the redirect_url set in the app config.
            code: A string containing the code to exchange.

        Returns:
            A dict.

        """
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_url,
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
        page = next((p for p in pages['data'] if p['id'] == page_id), None)
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

    def create_page_subscribed_apps(self, page_id, token):
        """

        Args:
            page_id:
            token:

        Returns:

        """
        params = self._get_params(token)
        return self._post('/{}/subscribed_apps'.format(page_id), params=params)

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
    def get_ad_leads(self, form_id, from_date=None, to_date=None, after=None):
        """Gets the leads for the given form.

        Args:
            form_id: A string with the Form's ID.
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
        return self._get('/{}/leads'.format(form_id), params=params)


    def get_custom_audience(self, id_account):
        """Get audiences for account_id

        :param account_id: Id for buissnes Id (get_account)

        :return: a Dict
        """

        params = self._get_params()
        params['fields'] = [ 'name']
        return self._get('/act_{}/customaudiences'.format(id_account),  params=params)

    def get_data_source_custom_audience(self, id_account):
        """Get audiences for account_id

        :param account_id: Id for buissnes Id (get_account)

        :return: a Dict
        """
        params = self._get_params()
        params['fields'] = ['data_source']
        return self._get('/act_{}/customaudiences'.format(id_account),  params=params)


    def get_adaccounts_id(self):
        """Get AdAccount for id user logged 
        

        :return: a Dict
        """

        params = self._get_params()
        params['fields'] = ['name']
        return self._get('/me/adaccounts', params=params)

    def create_ad_leads(self):
        raise NotImplementedError

    def get_ad_creatives(self):
        raise NotImplementedError

    def get_ad_copies(self):
        raise NotImplementedError

    def create_ad_copies(self):
        raise NotImplementedError

    def get_ad_insights(self):
        raise NotImplementedError

    def create_ad_insights(self):
        raise NotImplementedError

    def get_ad_keyword_stats(self):
        raise NotImplementedError

    def get_ad_previews(self):
        raise NotImplementedError

    def get_ad_targeting_sentence_lines(self):
        raise NotImplementedError

    def get_ad_account_activities(self):
        raise NotImplementedError

    def get_ad_account_ad_place_page_sets(self):
        raise NotImplementedError

    def create_ad_account_ad_place_page_sets(self):
        raise NotImplementedError

    def get_ad_account_ad_studies(self):
        raise NotImplementedError

    def get_ad_account_ad_asset_feeds(self):
        raise NotImplementedError

    def get_ad_account_ad_creatives(self):
        raise NotImplementedError

    def create_ad_account_ad_creatives(self):
        raise NotImplementedError

    def get_ad_account_ad_creatives_by_labels(self):
        raise NotImplementedError

    def get_ad_account_ad_images(self):
        raise NotImplementedError

    def create_ad_account_ad_images(self):
        raise NotImplementedError

    def delete_ad_account_ad_images(self):
        raise NotImplementedError

    def get_ad_account_ad_labels(self):
        raise NotImplementedError

    def create_ad_account_ad_labels(self):
        raise NotImplementedError

    def get_ad_account_ad_report_runs(self):
        raise NotImplementedError

    def get_ad_account_ad_report_schedules(self):
        raise NotImplementedError

    def get_ad_account_ad_rules_library(self):
        raise NotImplementedError

    def create_ad_account_ad_rules_library(self):
        raise NotImplementedError

    def get_ad_account_ads(self):
        raise NotImplementedError

    def create_ad_account_ads(self):
        raise NotImplementedError

    def get_ad_account_ads_by_label(self):
        raise NotImplementedError

    def get_ad_account_adsets(self):
        raise NotImplementedError

    def create_ad_account_adsets(self):
        raise NotImplementedError

    def get_ad_account_adsets_by_labels(self):
        raise NotImplementedError

    def get_ad_account_ads_pixel(self):
        raise NotImplementedError

    def create_ad_account_ads_pixel(self):
        raise NotImplementedError

    def get_ad_account_adtoplinedetails(self):
        raise NotImplementedError

    def get_ad_account_adtoplines(self):
        raise NotImplementedError

    def get_ad_account_advertisable_applications(self):
        raise NotImplementedError

    def get_ad_account_advideos(self):
        raise NotImplementedError

    def create_ad_account_advideos(self):
        raise NotImplementedError

    def get_ad_account_an_roas(self):
        raise NotImplementedError

    def get_ad_account_applications(self):
        raise NotImplementedError

    def get_ad_account_async_requests(self):
        raise NotImplementedError

    def get_ad_account_asyncadrequestsets(self):
        raise NotImplementedError

    def create_ad_account_asyncadrequestsets(self):
        raise NotImplementedError

    def get_ad_account_broadtargetingcategories(self):
        raise NotImplementedError

    def get_ad_account_business_activities(self):
        raise NotImplementedError

    def get_ad_account_campaigns(self):
        raise NotImplementedError

    def create_ad_account_campaigns(self):
        raise NotImplementedError

    def delete_ad_account_campaigns(self):
        raise NotImplementedError

    def get_ad_account_campaigns_by_label(self):
        raise NotImplementedError

    def get_ad_account_contextual_targeting_browse(self):
        raise NotImplementedError

    def get_ad_account_custom_audiences(self):
        raise NotImplementedError

    def create_ad_account_custom_audiences(self):
        raise NotImplementedError

    def get_ad_account_custom_audiencestos(self):
        raise NotImplementedError

    def get_ad_account_delivery_estimate(self):
        raise NotImplementedError

    def get_ad_account_generate_previews(self):
        raise NotImplementedError

    def get_ad_account_insights(self):
        raise NotImplementedError

    def create_ad_account_insights(self):
        raise NotImplementedError

    def get_ad_account_instagram_accounts(self):
        raise NotImplementedError

    def get_ad_account_minimum_budgets(self):
        raise NotImplementedError

    def get_ad_account_offline_conversion_data_sets(self):
        raise NotImplementedError

    def get_ad_account_offsitepixels(self):
        raise NotImplementedError

    def create_account_ad_offsitepixels(self):
        raise NotImplementedError

    def get_ad_account_partnercategories(self):
        raise NotImplementedError

    def get_ad_account_partners(self):
        raise NotImplementedError

    def get_ad_account_publisher_block_lists(self):
        raise NotImplementedError

    def create_ad_account_publisher_block_lists(self):
        raise NotImplementedError

    def get_ad_account_ratecard(self):
        raise NotImplementedError

    def get_ad_account_reachestimate(self):
        raise NotImplementedError

    def get_ad_account_reach_frequency_predictions(self):
        raise NotImplementedError

    def create_ad_account_reach_frequency_predictions(self):
        raise NotImplementedError

    def get_ad_account_roas(self):
        raise NotImplementedError

    def get_ad_account_rule_execution_history(self):
        raise NotImplementedError

    def get_ad_account_targeting_browse(self):
        raise NotImplementedError

    def get_ad_account_targeting_search(self):
        raise NotImplementedError

    def get_ad_account_targeting_sentence_lines(self):
        raise NotImplementedError

    def get_ad_account_targeting_suggestions(self):
        raise NotImplementedError

    def get_ad_account_targeting_validations(self):
        raise NotImplementedError

    def get_ad_account_targeting_tracking(self):
        raise NotImplementedError

    def create_ad_account_targeting_tracking(self):
        raise NotImplementedError

    def delete_ad_account_targeting_tracking(self):
        raise NotImplementedError

    def get_ad_account_targeting_transactions(self):
        raise NotImplementedError

    def get_ad_account_users(self):
        raise NotImplementedError

    # TODO Endpoints
    # Ad Creative
    # Image Ad
    # Previews
    # Ad Preview Plugin
    # Ad Set
    # Ad User
    # Ad Video
    # Campaign
    # Connection Objects
    # Currencies
    # Image Crop
    # Product Catalog

    def _get(self, endpoint, params=None):
        if self.BASE_URL in endpoint:
            raise Exception("The endpoint must not contain the facebook base URL.")
        response = requests.get(self.BASE_URL + endpoint, params=params)
        return self._parse(response.json())

    def _post(self, endpoint, params=None, data=None):
        response = requests.post(self.BASE_URL + endpoint, params=params, data=data)
        return self._parse(response.json())

    def _delete(self, endpoint, params=None):
        response = requests.delete(self.BASE_URL + endpoint, params=params)
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

        return response
