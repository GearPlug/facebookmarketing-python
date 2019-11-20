from facebookmarketing.decorators import access_token_required


class Instagram(object):
    def __init__(self, client):
        self._client = client

    @access_token_required
    def get_page(self, page_id, fields=None):
        """
        https://developers.facebook.com/docs/instagram-api/reference/page

        Args:
            page_id:
            fields:

        Returns:

        """
        params = self._client._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}'.format(page_id), params=params)

    @access_token_required
    def get_page_media(self, page_id, fields=None):
        """

        Args:
            page_id:
            fields:

        Returns:

        """
        params = self._client._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}/media'.format(page_id), params=params)

    @access_token_required
    def get_media_object(self, media_id, fields=None):
        """
        https://developers.facebook.com/docs/instagram-api/reference/media

        Args:
            media_id:
            fields:

        Returns:

        """
        params = self._client._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}'.format(media_id), params=params)

    @access_token_required
    def get_media_comment(self, media_id):
        """
        https://developers.facebook.com/docs/instagram-api/reference/media/comments

        Args:
            media_id:

        Returns:

        """
        params = self._client._get_params()
        return self._client._get('/{}/comments'.format(media_id), params=params)

    @access_token_required
    def get_hashtag_search(self, user_id, query):
        """
        https://developers.facebook.com/docs/instagram-api/reference/ig-hashtag-search

        Args:
            user_id:
            query:

        Returns:

        """
        params = self._client._get_params()
        params['user_id'] = user_id
        params['q'] = query
        return self._client._get('/ig_hashtag_search', params=params)

    @access_token_required
    def get_hashtag_object(self, hashtag_id, fields=None):
        """
        https://developers.facebook.com/docs/instagram-api/reference/hashtag

        Args:
            hashtag_id:
            fields:

        Returns:

        """
        params = self._client._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}'.format(hashtag_id), params=params)

    @access_token_required
    def get_hashtag_recent_media(self, hashtag_id, user_id, fields=None):
        """
        https://developers.facebook.com/docs/instagram-api/reference/hashtag/recent-media

        Args:
            hashtag_id:
            user_id:
            fields:

        Returns:

        """
        params = self._client._get_params()
        params['user_id'] = user_id
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}/recent_media'.format(hashtag_id), params=params)

    @access_token_required
    def get_hashtag_top_media(self, hashtag_id, user_id, fields=None):
        """
        https://developers.facebook.com/docs/instagram-api/reference/hashtag/top-media

        Args:
            hashtag_id:
            user_id:
            fields:

        Returns:

        """
        params = self._client._get_params()
        params['user_id'] = user_id
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}/top_media'.format(hashtag_id), params=params)
