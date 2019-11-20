class Insights(object):
    def __init__(self, client):
        self._client = client

    def get_insights(self, object_id, params=None, page_access_token=None):
        """
        https://developers.facebook.com/docs/graph-api/reference/v5.0/insights

        Returns:

        """
        params_ = self._client._get_params(page_access_token)
        if params:
            if not isinstance(params, dict):
                raise Exception('Params must be a dict.')

            params_.update(params)
        return self._client._get('/{}/insights/'.format(object_id), params=params_)
