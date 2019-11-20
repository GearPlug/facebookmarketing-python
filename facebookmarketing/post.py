class Post(object):
    def __init__(self, client):
        self._client = client

    def get_post_comments(self, post_id, fields=None, page_access_token=None):
        """
        https://developers.facebook.com/docs/graph-api/reference/post/comments/

        Returns:

        """
        params = self._client._get_params(page_access_token)
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}/comments'.format(post_id), params=params)
