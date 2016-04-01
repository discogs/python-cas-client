# -*- encoding: utf-8 -*-
from cas_client import CASClient, CASResponse
import unittest


class TestCase(unittest.TestCase):

    response_text = """
    <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
        <cas:authenticationSuccess>
            <cas:user>jott</cas:user>
            <cas:attributes>
                <cas:email>jott@purdue.edu</cas:email>
                <cas:i2a2characteristics>0,3592,2000</cas:i2a2characteristics>
                <cas:lastname>Ott</cas:lastname>
                <cas:firstname>Jeffrey A</cas:firstname>
                <cas:fullname>Jeffrey A Ott</cas:fullname>
                <cas:puid>0012345678</cas:puid>
            </cas:attributes>
        </cas:authenticationSuccess>
    </cas:serviceResponse>
    """

    slo_text = """
    <samlp:LogoutRequest
        xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
        xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
        ID="[RANDOM ID]"
        Version="2.0"
        IssueInstant="[CURRENT DATE/TIME]">
        <saml:NameID>@NOT_USED@</saml:NameID>
        <samlp:SessionIndex>[SESSION IDENTIFIER]</samlp:SessionIndex>
    </samlp:LogoutRequest>
    """

    def test_success(self):
        response = CASResponse(self.response_text)
        self.assertTrue(response.success)
        self.assertEqual(response.attributes, {
            u'i2a2characteristics': u'0,3592,2000',
            u'puid': u'0012345678',
            u'firstname': u'Jeffrey A',
            u'lastname': u'Ott',
            u'fullname': u'Jeffrey A Ott',
            u'email': u'jott@purdue.edu',
        })
        self.assertEqual(response.response_type, 'authenticationSuccess')
        self.assertEqual(response.user, 'jott')

    def test_failure(self):
        response = CASResponse(None)
        self.assertFalse(response.success)
        self.assertEqual(response.response_type, 'noResponse')

    def test_perform_service_validate(self):
        cas_client = CASClient('dummy.url')
        cas_client._request_cas_response = lambda url: self.response_text
        response = cas_client.perform_service_validate(
            ticket='FOO',
            service_url='BAR',
            )
        self.assertTrue(response.success)
        self.assertEqual(response.attributes, {
            u'i2a2characteristics': u'0,3592,2000',
            u'puid': u'0012345678',
            u'firstname': u'Jeffrey A',
            u'lastname': u'Ott',
            u'fullname': u'Jeffrey A Ott',
            u'email': u'jott@purdue.edu',
        })
        self.assertEqual(response.response_type, 'authenticationSuccess')
        self.assertEqual(response.user, 'jott')

    def test_get_login_url(self):
        cas_client = CASClient('dummy.url')
        service_url = 'app.url'
        url = cas_client.get_login_url(service_url=service_url)
        self.assertEqual(url, 'dummy.url/cas/login?service=app.url')

    def test_get_logout_url(self):
        cas_client = CASClient('dummy.url')
        service_url = 'app.url'
        url = cas_client.get_logout_url(service_url=service_url)
        self.assertEqual(url, 'dummy.url/cas/logout?service=app.url')

    def test_parse_logout_request(self):
        cas_client = CASClient('dummy.url')
        parsed_message = cas_client.parse_logout_request(self.slo_text)
        self.assertEqual(parsed_message, {
            'ID': '[RANDOM ID]',
            'IssueInstant': '[CURRENT DATE/TIME]',
            'Version': '2.0',
            'session_index': '[SESSION IDENTIFIER]',
            'xmlns:saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
            'xmlns:samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
        })
