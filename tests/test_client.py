from unittest import TestCase
from facebookmarketing.client import Client
from urllib.parse import urlparse, parse_qs


class FacebookMarketingTestCases(TestCase):
    def setUp(self):
        self.app_id = 0
        self.app_secret = ''
        self.client = Client(self.app_id, self.app_secret, 'v2.10')
        self.redirect_url = ''
        self.scope = ['manage_pages']

    def test_authorization_url(self):
        url = self.client.authorization_url(self.redirect_url, self.scope)
        self.assertIsInstance(url, str)
        o = urlparse(url)
        query = parse_qs(o.query)
        self.assertIn('client_id', query)
        self.assertEqual(query['client_id'][0], self.app_id)
        self.assertIn('redirect_uri', query)
        self.assertEqual(query['redirect_uri'][0], self.redirect_url)
        self.assertIn('scope', query)
        self.assertEqual(query['scope'], self.scope)

    def test_app_token(self):
        response = self.client.get_app_token()
        self.assertIsInstance(response, dict)
        self.assertIn('access_token', response)
        self.assertIn('token_type', response)
        self.assertEqual(response['token_type'], 'bearer')
