class Comment(object):
    def __init__(self, client):
        self._client = client

    def get_comment(self, comment_id, fields=None, page_access_token=None):
        """
        https://developers.facebook.com/docs/graph-api/reference/v5.0/comment

        Returns:

        """
        params = self._client._get_params(page_access_token)
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}'.format(comment_id), params=params)
