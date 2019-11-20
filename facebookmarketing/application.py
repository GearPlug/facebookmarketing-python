from urllib.parse import urlparse

from facebookmarketing import exceptions


class Application(object):
    def __init__(self, client):
        self._client = client

    def get_app_subscriptions(self, app_access_token):
        """
        https://developers.facebook.com/docs/graph-api/reference/v5.0/app/subscriptions

        Args:
            app_access_token:

        Returns:

        """
        params = self._client._get_params(app_access_token)
        return self._client._get('/{}/subscriptions'.format(self._client.app_id), params=params)

    def create_app_subscriptions(self, object_, callback_url, fields, verify_token, app_access_token):
        """
        You can create new Webhooks subscriptions using this edge:

        https://developers.facebook.com/docs/graph-api/reference/v5.0/app/subscriptions

        Args:
            object_:
            callback_url:
            fields:
            verify_token:
            app_access_token:

        Returns:

        """
        o = urlparse(callback_url)

        if o.scheme != 'https':
            raise exceptions.HttpsRequired

        params = self._client._get_params(app_access_token)
        params.update({
            'object': object_,
            'callback_url': callback_url,
            'fields': fields,
            'verify_token': verify_token
        })
        return self._client._post('/{}/subscriptions'.format(self._client.app_id), params=params)

    def delete_app_subscriptions(self, app_access_token):
        """
        You can delete all or per-object subscriptions using this operation:

        https://developers.facebook.com/docs/graph-api/reference/v5.0/app/subscriptions

        Args:
            app_access_token:

        Returns:

        """
        params = self._client._get_params(app_access_token)
        return self._client._delete('/{}/subscriptions'.format(self._client.app_id), params=params)
