import hashlib
import hmac
from hashlib import sha256
from urllib.parse import urlencode, urlparse
from uuid import uuid4

import requests

from facebookmarketing import exceptions
from facebookmarketing.decorators import access_token_required
from facebookmarketing.enumerators import ErrorEnum


class Client(object):
    BASE_URL = "https://graph.facebook.com/"

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        version: str = "v12.0",
        requests_hooks: dict = None,
        paginate: bool = True,
        limit: int = 100,
    ) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        if not version.startswith("v"):
            version = "v" + version
        self.version = version
        self.access_token = None
        self.paginate = paginate
        self.limit = limit
        self.BASE_URL += self.version
        if requests_hooks and not isinstance(requests_hooks, dict):
            raise Exception(
                'requests_hooks must be a dict. e.g. {"response": func}. http://docs.python-requests.org/en/master/user/advanced/#event-hooks'
            )
        self.requests_hooks = requests_hooks

    def set_access_token(self, token: str) -> None:
        """Sets the User Access Token for its use in this library.

        Args:
            token (str): User Access Token.
        """
        self.access_token = token

    def get_app_token(self) -> dict:
        """Generates an Application Token.

        Returns:
            dict: App token data.
        """
        params = {"client_id": self.app_id, "client_secret": self.app_secret, "grant_type": "client_credentials"}
        return self._get("/oauth/access_token", params=params)

    def authorization_url(self, redirect_uri: str, state: str, scope: list = None) -> str:
        """Generates an Authorization URL.

        Args:
            redirect_uri (str): A string with the redirect_url set in the app config.
            state (str): A unique code for validation.
            scope (list, optional): A list of strings with the scopes. Defaults to None.

        Raises:
            Exception: Scope argument is not a list.

        Returns:
            str: Url for oauth.
        """
        if scope is None:
            scope = []
        if not isinstance(scope, list):
            raise Exception("scope argument must be a list")

        params = {
            "client_id": self.app_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": " ".join(scope),
            "response_type": "code",
        }
        url = "https://facebook.com/{}/dialog/oauth?".format(self.version) + urlencode(params)
        return url

    def exchange_code(self, redirect_uri: str, code: str) -> dict:
        """Exchanges an oauth code for an user token.

        Args:
            redirect_uri (str): A string with the redirect_url set in the app config.
            code (str): A string containing the code to exchange.

        Returns:
            dict: User token data.
        """
        params = {
            "client_id": self.app_id,
            "redirect_uri": redirect_uri,
            "client_secret": self.app_secret,
            "code": code,
        }
        return self._get("/oauth/access_token", params=params)

    def extend_token(self, token: str) -> dict:
        """Extends a short-lived User Token for a long-lived User Token.

        Args:
            token (str): User token to extend.

        Returns:
            dict: User token data.
        """
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": token,
        }
        return self._get("/oauth/access_token", params=params)

    def inspect_token(self, input_token: str, token: str) -> dict:
        """Inspects an User Access Token.

        Args:
            input_token (str): A string with the User Access Token to inspect.
            token (str): A string with the Developer Token (App Owner) or an Application Token.

        Returns:
            dict: User token data.
        """
        params = {"input_token": input_token, "access_token": token}
        return self._get("/debug_token", params=params)

    @access_token_required
    def get_account(self) -> dict:
        """Gets the authed account information.

        Returns:
            dict: Account data.
        """
        params = self._get_params()
        return self._get("/me", params=params)

    @access_token_required
    def get_pages(self) -> dict:
        """Gets the authed account pages.

        Returns:
            dict: Pages data.
        """
        params = self._get_params()
        params["limit"] = self.limit
        return self._get("/me/accounts", params=params)

    @access_token_required
    def get_page_token(self, page_id: str) -> str:
        """Gets page token for the given page.

        Args:
            page_id (str): String with Page's ID.

        Returns:
            dict: Page token data.
        """
        pages = self.get_pages()
        page = next((p for p in pages["data"] if p["id"] == str(page_id)), None)
        if not page:
            return None
        return page["access_token"]

    def get_page_subscribed_apps(self, page_id: str, token: str) -> dict:
        """Get a list of apps subscribed to the Page's webhook updates.

        https://developers.facebook.com/docs/graph-api/reference/page/subscribed_apps/

        Args:
            page_id (str): Page's ID.
            token (str): Page's token.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params(token)
        return self._get("/{}/subscribed_apps".format(page_id), params=params)

    def create_page_subscribed_apps(self, page_id: str, token: str, params: dict = None) -> dict:
        """Associates an Application to a Page's webhook updates.

        https://developers.facebook.com/docs/graph-api/reference/page/subscribed_apps/

        Args:
            page_id (str): Page's ID.
            token (str): Page's token.
            params (dict, optional): Page Webhooks fields that you want to subscribe. Defaults to None.

        Returns:
            dict: Graph API Response.
        """
        _params = self._get_params(token)
        if params and isinstance(params, dict):
            _params.update(params)
        return self._post("/{}/subscribed_apps".format(page_id), params=_params)

    def delete_page_subscribed_apps(self, page_id: str, token: str) -> dict:
        """Dissociates an Application from a Page's webhook updates.

        https://developers.facebook.com/docs/graph-api/reference/page/subscribed_apps/

        Args:
            page_id (str): Page's ID.
            token (str): Page's token.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params(token)
        return self._delete("/{}/subscribed_apps".format(page_id), params=params)

    def get_app_subscriptions(self, application_token: str) -> dict:
        """Retrieves Webhook subscriptions for an App.

        https://developers.facebook.com/docs/graph-api/reference/v12.0/app/subscriptions

        Args:
            application_token (str): Application Token.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params(application_token)
        return self._get("/{}/subscriptions".format(self.app_id), params=params)

    def create_app_subscriptions(
        self, object: str, callback_url: str, fields: str, verify_token: str, token: str
    ) -> dict:
        """Creates a Webhook subscription for an App.

        https://developers.facebook.com/docs/graph-api/reference/v12.0/app/subscriptions

        Args:
            object (str): Indicates the object type that this subscription applies to.
            callback_url (str): The URL that will receive the POST request when an update is triggered.
            fields (str): The set of fields in this object that are subscribed to.
            verify_token (str): Indicates whether or not the subscription is active.
            token (str): Application Token.

        Raises:
            exceptions.HttpsRequired: callback_url is not https.

        Returns:
            dict: Graph API Response.
        """
        o = urlparse(callback_url)

        if o.scheme != "https":
            raise exceptions.HttpsRequired

        params = self._get_params(token)
        params.update({"object": object, "callback_url": callback_url, "fields": fields, "verify_token": verify_token})
        return self._post("/{}/subscriptions".format(self.app_id), params=params)

    def delete_app_subscriptions(self, token: str) -> dict:
        """Deletes a Webhook subscription for an App.

        https://developers.facebook.com/docs/graph-api/reference/v12.0/app/subscriptions

        Args:
            token (str): Application Token.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params(token)
        return self._delete("/{}/subscriptions".format(self.app_id), params=params)

    @access_token_required
    def get_ad_account_leadgen_forms(self, page_id: str, page_access_token: str = None) -> dict:
        """Gets the forms for the given page.

        Args:
            page_id (str): A string with Page's ID.
            page_access_token (str, optional): Page Access Token. Defaults to None.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params(token=page_access_token)
        params["limit"] = self.limit
        return self._get("/{}/leadgen_forms".format(page_id), params=params)

    @access_token_required
    def get_leadgen(self, leadgen_id: str, fields: list = None) -> dict:
        """Get a single leadgen given an id.

        Args:
            leadgen_id (str): A string with the leadgen's ID.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params()
        if fields:
            params["fields"] = ",".join(fields)
        return self._get("/{0}".format(leadgen_id), params=params)

    @access_token_required
    def get_ad_leads(
        self, leadgen_form_id: str, from_date: str = None, to_date: str = None, after: str = None, fields: list = None
    ) -> dict:
        """Gets the leads for the given form.

        Args:
            leadgen_form_id (str): A string with the Form's ID.
            from_date (str, optional): A timestamp. Defaults to None.
            to_date (str, optional): A timestamp. Defaults to None.
            after (str, optional): A cursor. Defaults to None.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params()
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        if after:
            params["after"] = after
        if fields:
            params["fields"] = ",".join(fields)
        return self._get("/{}/leads".format(leadgen_form_id), params=params)

    def get_custom_audience(self, account_id: str, fields: list = None) -> dict:
        """Retrieve a custom audience data.

        Args:
            account_id (str): Ad account id.
            fields (list, optional): Fields to include in the response. Defaults to None.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params["fields"] = ",".join(fields)
        return self._get("/{}/customaudiences".format(account_id), params=params)

    def create_custom_audience(
        self,
        account_id: str,
        name: str,
        description: str,
        subtype: str = "CUSTOM",
        customer_file_source: str = "USER_PROVIDED_ONLY",
    ) -> dict:
        """Create an empty Custom Audience.

        Args:
            account_id (str): Ad account id
            name (str): Custom Audience name
            description (str): Custom Audience description
            subtype (str): Type of Custom Audience
            customer_file_source (str): Describes how the customer information in your Custom Audience was originally collected.
                Values:
                USER_PROVIDED_ONLY
                Advertisers collected information directly from customers
                PARTNER_PROVIDED_ONLY
                Advertisers sourced information directly from partners (e.g., agencies or data providers)
                BOTH_USER_AND_PARTNER_PROVIDED
                Advertisers collected information directly from customers and it was also sourced from partners (e.g., agencies)

        https://developers.facebook.com/docs/marketing-api/audiences/guides/custom-audiences

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params()
        json = {
            "name": name,
            "description": description,
            "subtype": subtype,
            "customer_file_source": customer_file_source,
        }
        return self._post("/{}/customaudiences".format(account_id), params=params, json=json)

    def add_user_to_audience(self, audience_id: str, schema: str, data: list) -> dict:
        """Add people to your ad's audience with a hash of data from your business.

        https://developers.facebook.com/docs/marketing-api/reference/custom-audience/users/

        Args:
            audience_id (str): Audience id.
            schema (str): Specify what type of information you will be providing.
            data (list): List of data corresponding to the schema.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params()
        json = {
            "session": {
                "session_id": int(str(uuid4().int)[:7]),
                "batch_seq": 1,
                "last_batch_flag": True,
                "estimated_num_total": len(data),
            },
            "payload": {"schema": schema, "data": [sha256(i.encode("utf-8")).hexdigest() for i in data]},
        }
        return self._post("/{}/users".format(audience_id), params=params, json=json)

    def remove_user_to_audience(self, audience_id: str, schema: str, data: list) -> dict:
        """Remove people from your ad's audience with a hash of data from your business.

        https://developers.facebook.com/docs/marketing-api/reference/custom-audience/users/

        Args:
            audience_id (str): Audience id.
            schema (str): Specify what type of information you will be providing.
            data (list): List of data corresponding to the schema.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params()
        json = {
            "session": {
                "session_id": int(str(uuid4().int)[:7]),
                "batch_seq": 1,
                "last_batch_flag": True,
                "estimated_num_total": len(data),
            },
            "payload": {"schema": schema, "data": [sha256(i.encode("utf-8")).hexdigest() for i in data]},
        }
        return self._delete("/{}/users".format(audience_id), params=params, json=json)

    def get_adaccounts(self, fields: list = None) -> dict:
        """Retrieves Ad Accounts.

        Args:
            fields (list, optional): Fields to include in the response. Defaults to None.

        Returns:
            dict: Graph API Response.
        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params["fields"] = ",".join(fields)
        return self._get("/me/adaccounts", params=params)

    def get_instagram(self, page_id: str, fields: list = None) -> dict:
        """[summary]

        Args:
            page_id (str): [description]
            fields (list, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params["fields"] = ",".join(fields)
        return self._get("/{}".format(page_id), params=params)

    def get_instagram_media(self, page_id: str, fields: list = None) -> dict:
        """[summary]

        Args:
            page_id (str): [description]
            fields (list, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params["fields"] = ",".join(fields)
        return self._get("/{}/media".format(page_id), params=params)

    def get_instagram_media_object(self, media_id: str, fields: list = None) -> dict:
        """[summary]

        Args:
            media_id (str): [description]
            fields (list, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params["fields"] = ",".join(fields)
        return self._get("/{}".format(media_id), params=params)

    def get_instagram_media_comment(self, media_id: str) -> dict:
        """[summary]

        Args:
            media_id (str): [description]

        Returns:
            dict: [description]
        """
        params = self._get_params()
        return self._get("/{}/comments".format(media_id), params=params)

    def get_instagram_hashtag(self, page_id: str, fields: list = None) -> dict:
        """[summary]

        Args:
            page_id (str): [description]
            fields (list, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params["fields"] = ",".join(fields)
        return self._get("/{}/media".format(page_id), params=params)

    def get_instagram_hashtag_search(self, user_id: str, query: str) -> dict:
        """[summary]

        Args:
            user_id (str): [description]
            query (str): [description]

        Returns:
            dict: [description]
        """
        params = self._get_params()
        params["user_id"] = user_id
        params["q"] = query
        return self._get("/ig_hashtag_search", params=params)

    def get_instagram_hashtag_object(self, hashtag_id: str, fields: list = None) -> dict:
        """[summary]

        Args:
            hashtag_id (str): [description]
            fields (list, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """
        params = self._get_params()
        if fields and isinstance(fields, list):
            params["fields"] = ",".join(fields)
        return self._get("/{}".format(hashtag_id), params=params)

    def get_instagram_hashtag_recent_media(self, hashtag_id: str, user_id: str, fields: list = None) -> dict:
        """[summary]

        Args:
            hashtag_id (str): [description]
            user_id (str): [description]
            fields (list, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """
        params = self._get_params()
        params["user_id"] = user_id
        if fields and isinstance(fields, list):
            params["fields"] = ",".join(fields)
        return self._get("/{}/recent_media".format(hashtag_id), params=params)

    def get_instagram_hashtag_top_media(self, hashtag_id: str, user_id: str, fields: list = None) -> dict:
        """[summary]

        Args:
            hashtag_id (str): [description]
            user_id (str): [description]
            fields (list, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """
        params = self._get_params()
        params["user_id"] = user_id
        if fields and isinstance(fields, list):
            params["fields"] = ",".join(fields)
        return self._get("/{}/top_media".format(hashtag_id), params=params)

    def _get_params(self, token: str = None) -> dict:
        """Sets parameters for requests.

        Args:
            token (str, optional): Access token. Defaults to None.

        Returns:
            dict: Access token and hashed access token.
        """
        _token = token if token else self.access_token
        return {"access_token": _token, "appsecret_proof": self._get_app_secret_proof(_token)}

    def _get_app_secret_proof(self, token: str) -> str:
        """Generates app secret proof.

        https://developers.facebook.com/docs/graph-api/security

        Args:
            token (str): Access token to hash.

        Returns:
            str: Hashed access token.
        """
        key = self.app_secret.encode("utf-8")
        msg = token.encode("utf-8")
        h = hmac.new(key, msg=msg, digestmod=hashlib.sha256)
        return h.hexdigest()

    def _paginate_response(self, response: dict, **kwargs) -> dict:
        """Cursor-based Pagination

        https://developers.facebook.com/docs/graph-api/results

        Args:
            response (dict): Graph API Response.

        Returns:
            dict: Graph API Response.
        """
        if not self.paginate:
            return response
        while "paging" in response and "next" in response["paging"]:
            data = response["data"]
            params = kwargs.get("params", {})
            if "limit" in params:
                params.pop("limit")
            response = self._get(response["paging"]["next"].replace(self.BASE_URL, ""), **kwargs)
            response["data"] += data
        return response

    def _get(self, endpoint, **kwargs):
        return self._paginate_response(self._request("GET", endpoint, **kwargs), **kwargs)

    def _post(self, endpoint, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def _delete(self, endpoint, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)

    def _request(self, method, endpoint, headers=None, **kwargs):
        _headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if headers:
            _headers.update(headers)
        if self.requests_hooks:
            kwargs.update({"hooks": self.requests_hooks})
        return self._parse(requests.request(method, self.BASE_URL + endpoint, headers=_headers, **kwargs))

    def _parse(self, response):
        if "application/json" in response.headers["Content-Type"]:
            r = response.json()
        else:
            return response.text

        if "error" in r:
            error = r["error"]
        elif "data" in r and "error" in r["data"]:
            error = r["data"]["error"]
        else:
            error = None

        if error:
            code = error["code"]
            message = error["message"]
            try:
                error_enum = ErrorEnum(code)
            except Exception:
                raise exceptions.UnexpectedError("Error: {}. Message {}".format(code, message))
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
                raise exceptions.BaseError("Error: {}. Message {}".format(code, message))

        return r
