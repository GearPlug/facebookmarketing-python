from facebookmarketing.decorators import access_token_required


class Marketing(object):
    def __init__(self, client):
        self._client = client

    @access_token_required
    def get_leadgen(self, leadgen_id):
        """
        A LeadGen submission by a user via a Feed Ad unit

        https://developers.facebook.com/docs/marketing-api/reference/user-lead-gen-info/

        Args:
            leadgen_id:

        Returns:

        """
        params = self._client._get_params()
        return self._client._get('/{0}'.format(leadgen_id), params=params)

    @access_token_required
    def get_ad_leads(self, leadgen_form_id, from_date=None, to_date=None, after=None):
        """
        https://developers.facebook.com/docs/marketing-api/reference/adgroup/leads/

        Args:
            leadgen_form_id:
            from_date:
            to_date:
            after:

        Returns:

        """
        params = self._client._get_params()
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
        if after:
            params['after'] = after
        return self._client._get('/{}/leads'.format(leadgen_form_id), params=params)

    @access_token_required
    def get_custom_audience(self, account_id, fields=None):
        """
        https://developers.facebook.com/docs/marketing-api/reference/ad-account/customaudiences/

        Args:
            account_id:
            fields:

        Returns:

        """
        params = self._client._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/{}/customaudiences'.format(account_id), params=params)

    @access_token_required
    def get_adaccounts_id(self, fields=None):
        """
        The advertising accounts to which this person has access

        https://developers.facebook.com/docs/marketing-api/reference/custom-audience/adaccounts/

        Returns:

        """
        params = self._client._get_params()
        if fields and isinstance(fields, list):
            params['fields'] = ','.join(fields)
        return self._client._get('/me/adaccounts', params=params)
