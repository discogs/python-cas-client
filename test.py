# -*- encoding: utf-8 -*-
from cas_client import CASResponse
import unittest


class TestCase(unittest.TestCase):

    def test_success(self):
        response = """
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
        response = CASResponse(response)
        self.assertTrue(response.success)
        self.assertEqual(response.attributes, {
            u'i2a2characteristics': u'0,3592,2000',
            u'puid': u'0012345678',
            u'firstname': u'Jeffrey A',
            u'lastname': u'Ott',
            u'fullname': u'Jeffrey A Ott',
            u'email': u'jott@purdue.edu',
        })
        self.assertEqual(response.proxy_granting_ticket, None)
        self.assertEqual(response.proxy_ticket, None)
        self.assertEqual(response.response_type, 'authenticationSuccess')
        self.assertEqual(response.user, 'jott')

    def test_failure(self):
        response = CASResponse(None)
        self.assertFalse(response.success)
        self.assertEqual(response.response_type, 'noResponse')
