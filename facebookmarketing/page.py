from facebookmarketing.decorators import access_token_required


class Page(object):
    def __init__(self, client):
        self._client = client

    def get_page_subscribed_apps(self, page_id, page_access_token):
        """
        https://developers.facebook.com/docs/graph-api/reference/page/subscribed_apps/

        Args:
            page_id:
            page_access_token:

        Returns:

        """
        params = self._client._get_params(page_access_token)
        return self._client._get('/{}/subscribed_apps'.format(page_id), params=params)

    def create_page_subscribed_apps(self, page_id, page_access_token, params=None):
        """
        When you create a subscribed_apps edge, the page-id you use in endpoint must match the page ID of the page
        access token used in the API call. The app that the access token is for is installed for the page.

        Note that you cannot use this edge's subscribed_fields parameter to configure or subscribe to Webhooks for
        Instagram fields; you must use your app's dashboard instead.

        You can make a POST request to subscribed_apps edge from the following paths:
        /{page_id}/subscribed_apps
        When posting to this edge, a Page will be created.

        https://developers.facebook.com/docs/graph-api/reference/page/subscribed_apps/

        Args:
            page_id:
            page_access_token:
            params:

        Returns:

        """
        params_ = self._client._get_params(page_access_token)
        if params:
            if not isinstance(params, dict):
                raise Exception('Params must be a dict.')

            params_.update(params)
        return self._client._post('/{}/subscribed_apps'.format(page_id), params=params_)

    def delete_page_subscribed_apps(self, page_id, page_access_token):
        """
        https://developers.facebook.com/docs/graph-api/reference/page/subscribed_apps/

        Args:
            page_id:
            page_access_token:

        Returns:

        """
        params = self._client._get_params(page_access_token)
        return self._client._delete('/{}/subscribed_apps'.format(page_id), params=params)

    def get_ad_account_leadgen_forms(self, page_id, page_access_token=None):
        """
        Fetch LeadGen forms associated with a page

        https://developers.facebook.com/docs/graph-api/reference/page/leadgen_forms/

        Args:
            page_id:
            page_access_token:

        Returns:

        """
        params = self._client._get_params(page_access_token)
        new_result = self._client._get('/{}/leadgen_forms'.format(page_id), params=params)
        del params['access_token']  # Las urls siguiente ya incluyen el access token, pero no el proof.
        form_list = new_result['data']
        while 'paging' in new_result and 'next' in new_result['paging']:
            # La URL de next incluye el base, lo cambiamos a ''.
            new_result = self._client._get(new_result['paging']['next'].replace(self._client.BASE_URL, ''),
                                           params=params)
            form_list += new_result['data']
        return {'data': form_list}

    @access_token_required
    def get_page_feed(self, page_id, paginate=True):
        """
        https://developers.facebook.com/docs/graph-api/reference/v5.0/page/feed

        Returns:

        """
        params = self._client._get_params()
        if not paginate:
            return self._client.get_unpaginated_result('/{}/feed'.format(page_id), params)
        return self._client._get('/{}/feed'.format(page_id), params=params)
