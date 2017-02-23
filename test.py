# -*- encoding: utf-8 -*-
import unittest
from cas_client import CASClient, CASResponse
try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs


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

    slo_text_2 = """
    <samlp:LogoutRequest
        xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
        xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
        ID="935a2d0c-4026-481e-be3d-20a1b2cdd553"
        Version="2.0"
        IssueInstant="2016-04-08 00:40:55 +0000">
        <saml:NameID>@NOT_USED@</saml:NameID>
        <samlp:SessionIndex>ST-14600760351898-0B3lSFt2jOWSbgQ377B4CtbD9uq0MXR9kG23vAuH</samlp:SessionIndex>
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
        cas_client = CASClient('https://dummy.url')
        cas_client._perform_get = lambda url: self.response_text
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

    def test_get_destroy_other_sessions_url(self):
        cas_client = CASClient('https://dummy.url')
        service_url = 'https://app.url'
        url = cas_client.get_destroy_other_sessions_url(service_url=service_url)
        self.assertEqual(url, 'https://dummy.url/cas/destroy-other-sessions?service=https://app.url')

    def test_get_login_url(self):
        cas_client = CASClient('https://dummy.url')
        service_url = 'https://app.url'
        url = cas_client.get_login_url(service_url=service_url)
        self.assertEqual(url, 'https://dummy.url/cas/login?service=https://app.url')

    def test_get_logout_url(self):
        cas_client = CASClient('https://dummy.url')
        service_url = 'https://app.url'
        url = cas_client.get_logout_url(service_url=service_url)
        self.assertEqual(url, 'https://dummy.url/cas/logout?service=https://app.url')

    def test_parse_logout_request(self):
        cas_client = CASClient('https://dummy.url')
        parsed_message = cas_client.parse_logout_request(self.slo_text)
        self.assertEqual(parsed_message, {
            'ID': '[RANDOM ID]',
            'IssueInstant': '[CURRENT DATE/TIME]',
            'Version': '2.0',
            'session_index': '[SESSION IDENTIFIER]',
            'xmlns:saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
            'xmlns:samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
        })

    def test_parse_logout_request_2(self):
        cas_client = CASClient('https://dummy.url')
        parsed_message = cas_client.parse_logout_request(self.slo_text_2)
        self.assertEqual(parsed_message, {
            'ID': '935a2d0c-4026-481e-be3d-20a1b2cdd553',
            'IssueInstant': '2016-04-08 00:40:55 +0000',
            'Version': '2.0',
            'session_index': 'ST-14600760351898-0B3lSFt2jOWSbgQ377B4CtbD9uq0MXR9kG23vAuH',
            'xmlns:saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
            'xmlns:samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
        })

    def test_get_api_url(self):
        cas_client = CASClient('https://dummy.url')
        api_resource = 'do_something_useful'
        auth_token_ticket = 'ATT-1234'
        authenticator = 'my_company_ldap'
        private_key_filepath = 'test_private_key.pem'
        with open(private_key_filepath, 'r') as file_pointer:
            private_key = file_pointer.read()
        service_url = 'https://example.com'
        kwargs = {
            'and': 'another_thing',
            'you': 'should_know',
            }
        url = cas_client.get_api_url(
            api_resource=api_resource,
            auth_token_ticket=auth_token_ticket,
            authenticator=authenticator,
            private_key=private_key,
            service_url=service_url,
            **kwargs
            )
        query_string = url.partition('?')[-1]
        query_parameters = {
            key: value[0]
            for key, value in parse_qs(query_string).items()
        }
        assert query_parameters == {
            'at': (
                'eyJhbmQiOiAiYW5vdGhlcl90aGluZyIsICJhdXRoZW50aWNhdG9yIjogIm15'
                'X2NvbXBhbnlfbGRhcCIsICJ0aWNrZXQiOiAiQVRULTEyMzQiLCAieW91Ijog'
                'InNob3VsZF9rbm93In0='
                ),
            'ats': (
                'FISMx+fVfKKzI160MQRMauKdeqBRzzg+Ihwh0WqhqcnW4d+S0IyrTg6/oY1a'
                'wGvhBGrSMzOEBfYyihj5SxmLMr+xWm5Ndt+m0WcjuOR2GEwtEimIbbEQslCu'
                'f+//tG2u3UacStBRctt/cWnIGlW9cIPlUgU4iVVQtpbC7DdJc9+2rwzN10jV'
                '36JUwAWWT3iQseTiyMy+Bbuu1bzTcdtKvBdHTnCwcu1m9vkQraH/ZuVbYVMB'
                'jZC1s5lXECLN+fnC00laglYmgQ1w59EoQIXuaaHFqgq+zRvRxm4r0ASG5F0D'
                'bPT0fEDihQulSAbyOY5/6nhkFq6NYlJADKuGchFusk9D3Pcgs2KyEW3xvBb4'
                'ZArn2oaI8sxjOYUXutf1xe5MBGy8oTW+3QbHVv+hzXOrwJXsbSz6bx3gmDYb'
                'bDilhbRgPQeTH17IwqArrVgnjgcAMoDk6cTqU548S19KMc8B99pVZ7JMM5Ls'
                'uKx/ZWUF0naXFeuEaFJ5TdaO6HhhiRhUAEwlnwTQwwJuR1VtcYx4z3Lb5NhN'
                'CtH658M8acru4Dv4jV5NC3IPJcCijKGVjZQ0K6GrD863fr3usnH1gvnTzNgJ'
                '1jijF4FmyIr8E9kpNM5Mk7D0AqSGCC2nZcu/r4+2rcLiq9XxViv3jpe44alQ'
                'RjhkcqcbkcJvnhckfgjrU7w='
                ),
            'service': 'https://example.com',
            }

    def test_get_auth_token_login_url(self):
        cas_client = CASClient('https://dummy.url')
        auth_token_ticket = 'AT-1234'
        authenticator = 'my_company_ldap'
        username = 'my_user'
        service_url = 'https://example.com'
        private_key_filepath = 'test_private_key.pem'
        with open(private_key_filepath, 'r') as file_pointer:
            private_key = file_pointer.read()
        url = cas_client.get_auth_token_login_url(
            auth_token_ticket=auth_token_ticket,
            authenticator=authenticator,
            private_key=private_key,
            service_url=service_url,
            username=username,
            )
        query_string = url.partition('?')[-1]
        query_parameters = {
            key: value[0]
            for key, value in parse_qs(query_string).items()
        }
        assert query_parameters == {
            'at': (
                'eyJhdXRoZW50aWNhdG9yIjogIm15X2NvbXBhbnlfbGRhcCIsICJ0aWNrZXQi'
                'OiAiQVQtMTIzNCIsICJ1c2VybmFtZSI6ICJteV91c2VyIn0='
                ),
            'ats': (
                'pZ3m58k8Xpd+TDlYb+VDV89TVGoPIAgsxDMNGtNLqzchg/EFy12NzVaUbVSz'
                '1PNZdQ/klMrfvxzehLlFp9QkyfFoUS5pgUo9XXjpowWe0E9eKX5hBJjpmvD+'
                'PhSMRXFOPUOLRohRX45aPqJ4mjh2MNP0mzKrRfoRoUT/6mmrvLRJu150rtnS'
                'A5E4n0V4BeJXWIFYqqu8B4CP3fbg18HMB5g36P61m6I67kDmBLfTlmtrwvM5'
                'Vh3r9q9HFGn1NGmdMTcqGwAqfrww2XuBBemTpcfvSLNhTf/nZ21042BDt0+J'
                'TLNsGBxNKS39NznyOcf2g5XtscdJXcDcKan/eJI7WHNtpmJPzhA4H5wTuAm7'
                'X0WgAN7hxmTYy3E0241j6Q1DNDuxvgkSMS7CJhD3p0Fp0kHsdCslLuqjMoou'
                'THSshfJU6lvE4dc1vh3fdzKiAcmvMQ2RT4ACNQVwVYiE9UWu23D16yz08sV2'
                '9kzlFTCTXT608tHMVCx1x7K959IxcRUFld314ooqJ5BgrK/2QqtZXS0w581f'
                '8P5qViQoOrQ5gRiPZ/bT6eF24RLuKN78VEkak2z0B1aZqpEcG3wQC4qHeUaM'
                'TgrihbVi6eIv7N5k6srSyGCAQ/9k7o53ZKG8MzkqMJq53AoEXNj8HNQxgO0D'
                'OtFwXLMrlrFpmqPS5OcO9NM='
                ),
            'service': 'https://example.com',
            }
