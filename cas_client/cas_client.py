# -*- encoding: utf-8 -*-
import requests
from xml.dom.minidom import parseString


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


class CASClient(object):

    def __init__(
        self,
        server_url,
        service_url,
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

    def get_login_url(self):
        template = '{server_url}{auth_prefix}/login?service={service_url}'
        return template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            service_url=self.service_url,
            )

    def get_logout_url(self):
        template = '{server_url}{auth_prefix}/logout?service={service_url}'
        return template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            service_url=self.service_url,
            )

    def perform_proxy(self, proxy_ticket=None):
        url = self._get_proxy_url(proxy_ticket)
        return self._perform_cas_call(url, proxy_ticket)

    def perform_proxy_validate(self, proxied_service_ticket=None):
        url = self._get_proxy_url(proxied_service_ticket)
        return self._perform_cas_call(url, proxied_service_ticket)

    def perform_service_validate(self, ticket=None):
        url = self._get_service_validate_url(ticket)
        return self._perform_cas_call(url, ticket)

    def reauthenticate(self, proxy_granting_ticket, username=None):
        if not proxy_granting_ticket:
            return False, None
        proxy_response = self.perform_proxy(proxy_granting_ticket)
        proxy_ticket = proxy_response.proxy_ticket
        if proxy_response.error:
            return False, proxy_response
        elif not proxy_response.data:
            raise Exception
        elif not proxy_ticket:  # Can this be consolidated?
            return False, proxy_response
        validate_response = self.perform_proxy_validate(proxy_ticket)
        if validate_response.error:
            raise Exception
        elif not validate_response.data:
            raise Exception
        elif not validate_response.user:
            return False, validate_response
        success = username == validate_response.user if username else True
        return success, validate_response

    ### PRIVATE METHODS ###

    def _get_proxy_url(self, ticket):
        template = '{server_url}{auth_prefix}/proxy?'
        template += 'targetService={proxy_callback}&pgt={ticket}'
        return template.format(
            auth_prefix=self.auth_prefix,
            proxy_callback=self.proxy_callback,
            server_url=self.server_url,
            ticket=ticket,
            )

    def _get_proxy_validate_url(self, ticket):
        template = '{server_url}{auth_prefix}/proxyValidate?'
        template += 'ticket={ticket}&pgt={proxy_callback}'
        return template.format(
            auth_prefix=self.auth_prefix,
            proxy_callback=self.proxy_callback,
            server_url=self.server_url,
            ticket=ticket,
            )

    def _get_service_validate_url(self, ticket):
        template = '{server_url}{auth_prefix}/serviceValidate?'
        template += 'ticket={ticket}&service={service_url}'
        return template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            ticket=ticket,
            service_url=self.service_url,
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


__all__ = ['CASClient', 'CASResponse']
