from facebookmarketing.decorators import access_token_required


class User(object):
    def __init__(self, client):
        self._client = client

    @access_token_required
    def get_account(self):
        """
        Gets a User.

        https://developers.facebook.com/docs/graph-api/reference/user/

        Returns:

        """
        params = self._client._get_params()
        return self._client._get('/me', params=params)

    @access_token_required
    def get_pages(self):
        """
        Pages the User has a role on

        https://developers.facebook.com/docs/graph-api/reference/user/accounts/

        Returns:

        """
        params = self._client._get_params()
        new_result = self._client._get('/me/accounts', params=params)
        del params['access_token']  # Las urls siguiente ya incluyen el access token, pero no el proof.
        page_list = new_result['data']
        while 'paging' in new_result and 'next' in new_result['paging']:
            # La URL de next incluye el base, lo cambiamos a ''.
            new_result = self._client._get(new_result['paging']['next'].replace(self._client.BASE_URL, ''),
                                           params=params)
            page_list += new_result['data']
        return {'data': page_list}  # Se retorna un dict con el key data para mantener compatibilidad.

    @access_token_required
    def get_page_token(self, page_id):
        """

        Args:
            page_id:

        Returns:

        """
        pages = self.get_pages()
        page = next((p for p in pages['data'] if p['id'] == page_id), None)
        if not page:
            return None

        return page['access_token']

    def get_user(self, user_id, fields=None, page_access_token=None):
        """
        Gets a User.

        https://developers.facebook.com/docs/graph-api/reference/user/

        Returns:

        """
        params = self._client._get_params(page_access_token)
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}'.format(user_id), params=params)

    def get_user_picture(self, user_id, fields=None, page_access_token=None):
        """
        https://developers.facebook.com/docs/graph-api/reference/user/picture/

        Returns:

        """
        params = self._client._get_params(page_access_token)
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        params['type'] = 'large'
        return self._client._get('/{}/picture'.format(user_id), params=params)
