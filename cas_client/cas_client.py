# -*- encoding: utf-8 -*-
import logging
import requests
from xml.dom.minidom import parseString


class CASClient(object):

    def __init__(
        self,
        server_url,
        service_url=None,
        auth_prefix='/cas',
        proxy_url=None,
        proxy_callback=None,
        verify_certificates=False,
        ):
        self.auth_prefix = auth_prefix
        self.proxy_callback = proxy_callback
        self.proxy_url = proxy_url
        self.server_url = server_url
        self.service_url = service_url
        self.verify_certificates = bool(verify_certificates)

    ### PUBLIC METHODS ###

    def get_login_url(self, service_url=None):
        template = '{server_url}{auth_prefix}/login?service={service_url}'
        url = template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            service_url=service_url or self.service_url,
            )
        logging.debug('[CAS] Login URL: {}'.format(url))
        return url

    def get_logout_url(self, service_url=None):
        template = '{server_url}{auth_prefix}/logout?service={service_url}'
        url = template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            service_url=service_url or self.service_url,
            )
        logging.debug('[CAS] Logout URL: {}'.format(url))
        return url

    def perform_proxy(self, proxy_ticket):
        url = self._get_proxy_url(ticket=proxy_ticket)
        logging.debug('[CAS] Proxy URL: {}'.format(url))
        return self._perform_cas_call(url, ticket=proxy_ticket)

    def perform_proxy_validate(self, proxied_service_ticket):
        url = self._get_proxy_validate_url(ticket=proxied_service_ticket)
        logging.debug('[CAS] ProxyValidate URL: {}'.format(url))
        return self._perform_cas_call(url, ticket=proxied_service_ticket)

    def perform_service_validate(self, ticket=None, service_url=None):
        url = self._get_service_validate_url(ticket, service_url=service_url)
        logging.debug('[CAS] ServiceValidate URL: {}'.format(url))
        return self._perform_cas_call(url, ticket=ticket)

    ### PRIVATE METHODS ###

    def _get_proxy_url(self, ticket):
        template = '{server_url}{auth_prefix}/proxy?'
        template += 'targetService={proxy_callback}&pgt={ticket}'
        url = template.format(
            auth_prefix=self.auth_prefix,
            proxy_callback=self.proxy_callback,
            server_url=self.server_url,
            ticket=ticket,
            )
        return url

    def _get_proxy_validate_url(self, ticket):
        template = '{server_url}{auth_prefix}/proxy?'
        template += 'ticket={ticket}&service={proxy_callback}'
        url = template.format(
            auth_prefix=self.auth_prefix,
            proxy_callback=self.proxy_callback,
            server_url=self.server_url,
            ticket=ticket,
            )
        return url

    def _get_service_validate_url(self, ticket, service_url=None):
        template = '{server_url}{auth_prefix}/serviceValidate?'
        template += 'ticket={ticket}&service={service_url}'
        url = template.format(
            auth_prefix=self.auth_prefix,
            server_url=self.server_url,
            service_url=service_url or self.service_url,
            ticket=ticket,
            )
        if self.proxy_url:
            url = '{url}&pgtUrl={proxy_url}'.format(url, self.proxy_url)
        return url

    def _perform_cas_call(self, url, ticket):
        if ticket is not None:
            logging.debug('[CAS] Requesting Ticket Validation')
            response_text = self._request_cas_response(url)
            response_text = self._clean_up_response_text(response_text)
            if response_text:
                logging.debug('[CAS] Response:\n{}'.format(response_text))
                return CASResponse(response_text)
        logging.debug('[CAS] Response: None')
        return None

    def _clean_up_response_text(self, response_text):
        lines = []
        for line in response_text.splitlines():
            line = line.rstrip()
            if line:
                lines.append(line)
        return '\n'.join(lines)

    def _request_cas_response(self, url):
        try:
            response = requests.get(url, verify=self.verify_certificates)
            return response.text
        except requests.HTTPError:
            return None


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
