# -*- encoding: utf-8 -*-
import requests
from xml.dom.minidom import parseString


class CASClient(object):

    def __init__(
        self,
        server_url,
        service_url=None,
        proxy_url=None,
        proxy_callback_url=None,
        auth_prefix='/cas',
        verify_certificates=False,
        ):
        self.auth_prefix = auth_prefix
        self.proxy_url = proxy_url
        self.proxy_callback_url = proxy_callback_url
        self.server_url = server_url
        self.service_url = service_url
        self.verify_certificates = bool(verify_certificates)

    ### PUBLIC METHODS ###

    def get_login_url(self, service_url=None):
        template = '{server_url}{auth_prefix}/login?service={service_url}'
        return template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            service_url=service_url or self.service_url,
            )

    def get_logout_url(self, service_url=None):
        template = '{server_url}{auth_prefix}/logout?service={service_url}'
        return template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            service_url=service_url or self.service_url,
            )

    def perform_service_validate(self, ticket=None, service_url=None):
        url = self._get_service_validate_url(ticket, service_url=service_url)
        return self._perform_cas_call(url, ticket=ticket)

    ### PRIVATE METHODS ###

    def _get_service_validate_url(self, ticket, service_url=None):
        template = '{server_url}{auth_prefix}/serviceValidate?'
        template += 'ticket={ticket}&service={service_url}'
        return template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            ticket=ticket,
            service_url=service_url or self.service_url,
            )

    def _perform_cas_call(self, url, ticket):
        cas_type, cas_data = None, {}
        if ticket is not None:
            response = self._request_cas_response(url)
            cas_type, cas_data = self._parse_cas_xml_response(response)
        return cas_type, cas_data

    def _request_cas_response(self, url):
        try:
            response = requests.get(url, verify=self.verify_certificates)
            return response.text
        except requests.HTTPError:
            pass


class CASResponse(object):

    def __init__(self, response_text):
        self.response_text = response_text
        self.response_type, cas_data = self._parse_cas_xml_response(
            response_text)
        self.success = 'success' in self.response_type.lower()
        self.data = cas_data.get(self.response_type)
        if isinstance(self.data, dict):
            self.error = None
        else:
            self.data = {}
            self.error = cas_data
        self.user = self.data.get('user')
        self.attributes = self.data.get('attributes')
        self.proxy_granting_ticket = self.data.get('proxyGrantingTicket')
        self.proxy_ticket = self.data.get('proxyTicket')

    @classmethod
    def _parse_cas_xml_response(cls, response_text):
        cas_type = 'noResponse'
        cas_data = {}
        if not response_text:
            return cas_type, cas_data
        xml_document = parseString(response_text)
        node_element = xml_document.documentElement
        if node_element.nodeName != 'cas:serviceResponse':
            raise Exception
        for child in node_element.childNodes:
            if child.nodeType != child.ELEMENT_NODE:
                continue
            cas_type = child.nodeName.replace("cas:", "")
            cas_data = cls._parse_cas_xml_data(child)
            break
        return cas_type, cas_data

    @classmethod
    def _parse_cas_xml_data(cls, xml_node):
        result = {}
        tag_name = xml_node.nodeName.replace('cas:', '')
        for child in xml_node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                text = child.nodeValue.strip()
                if text:
                    result[tag_name] = text
            elif child.nodeType == child.ELEMENT_NODE:
                subresult = cls._parse_cas_xml_data(child)
                result.setdefault(tag_name, {}).update(subresult)
        return result


__all__ = [
    'CASClient',
    'CASResponse'
    ]
