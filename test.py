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

    def test_get_auth_token_logic_url(self):
        cas_client = CASClient('dummy.url')
        auth_token_ticket = 'AT-1234'
        authenticator = 'my_company_ldap'
        username = 'my_user'
        service_url = 'example.com'
        private_key_filepath = 'test_private_key.pem'
        url = cas_client.get_auth_token_login_url(
            auth_token_ticket=auth_token_ticket,
            authenticator=authenticator,
            private_key_filepath=private_key_filepath,
            service_url=service_url,
            username=username,
            )
        self.assertEqual(url,
            'dummy.url/cas/authTokenLogin?at=eyJhdXRoZW50aWNhdG9yIjogIm15X2Nvb'
            'XBhbnlfbGRhcCIsICJ1c2VybmFtZSI6ICJteV91c2VyIiwgInRpY2tldCI6ICJBVC'
            '0xMjM0In0=&ats=k9cALH8BBpq2cfyGWe3CRovnvPVaQHAlUINW8JnQ4xpgjaSdh6'
            'ZSMX8IbVA9qscMogxWlZbYA569a9eotU9gAZ/0awRi+g1lazCs8svGIWYKNIvhtUO'
            'DQ3yt1n1kf33Wh7EbRnWuTL3A1nI0Rfy0e9uW8W6I7YYhr6BrrXiZVPGjM0V9uVOG'
            'RVci0majogL1WseMs1f2DNusu3Ep3umHEagt56X3QiRBnuSzE9cTPN5TGf5WH76BZ'
            '3YpW7hYkAA8aRlG+LXO+XGYtCz3qfzqiPEXYrIbc0+u8PcAvsBmgMQmgCbwQ3rBM5'
            'C8FQrb8Sn3WAk5lSb1j55M0C51dHAEut9q2dH+SwDJp4rmi3Iw0RlV4rTXhdf73eH'
            'WfF94JCjOPoarkvZqOFGvhgZarmg3ZY/PDIUZ4sckVlzsTumADmEdz5R1rPjfgJMo'
            's6l0F+EfswikR7WgkaMm3XYCS+iVwY0wVIlT/vYkxPoTfYGjR/1z3YQdko0wVXnII'
            'pn1WENl+8Ggct5kLbHsgUH+RB6kGjkAjHbp4a7PrR3SQtJjl5M6sQuX6ol4Xt7vWN'
            'aAP3XwceqTi5IeN9htFRWi+uRIPfN9+Q41Z5WivA9Ettb87r/8eDJqGTaTgIn6hY8'
            '7vtyFnBsaz5KDRtr0rgA3y/uvhb/ztFkO6jPpDLxiVVqlwnw=&service=example'
            '.com')
