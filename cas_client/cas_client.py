# -*- encoding: utf-8 -*-
import abc
import json
import logging
import requests
from xml.dom.minidom import parseString


class CASClient(object):
    r'''A client for interacting with a remote CAS instance.'''

    def __init__(
        self,
        server_url,
        service_url=None,
        auth_prefix='/cas',
        proxy_url=None,
        proxy_callback=None,
        verify_certificates=False,
        session_storage_adapter=None,
        ):
        self._auth_prefix = auth_prefix
        self._proxy_callback = proxy_callback
        self._proxy_url = proxy_url
        self._server_url = server_url
        self._service_url = service_url
        self._session_storage_adapter = session_storage_adapter
        self._verify_certificates = bool(verify_certificates)

    ### PUBLIC METHODS ###

    def get_login_url(self, service_url=None):
        r'''Get the URL for a remote CAS `login` endpoint.'''
        template = '{server_url}{auth_prefix}/login?service={service_url}'
        url = template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            service_url=service_url or self.service_url,
            )
        logging.debug('[CAS] Login URL: {}'.format(url))
        return url

    def get_logout_url(self, service_url=None):
        r'''Get the URL for a remote CAS `logout` endpoint.'''
        template = '{server_url}{auth_prefix}/logout?service={service_url}'
        url = template.format(
            server_url=self.server_url,
            auth_prefix=self.auth_prefix,
            service_url=service_url or self.service_url,
            )
        logging.debug('[CAS] Logout URL: {}'.format(url))
        return url

    def perform_proxy(self, proxy_ticket):
        r'''Fetch a response from the remote CAS `proxy` endpoint.'''
        url = self._get_proxy_url(ticket=proxy_ticket)
        logging.debug('[CAS] Proxy URL: {}'.format(url))
        return self._perform_cas_call(url, ticket=proxy_ticket)

    def perform_proxy_validate(self, proxied_service_ticket):
        r'''Fetch a response from the remote CAS `proxyValidate` endpoint.'''
        url = self._get_proxy_validate_url(ticket=proxied_service_ticket)
        logging.debug('[CAS] ProxyValidate URL: {}'.format(url))
        return self._perform_cas_call(url, ticket=proxied_service_ticket)

    def perform_service_validate(self, ticket=None, service_url=None):
        r'''Fetch a response from the remote CAS `serviceValidate` endpoint.'''
        url = self._get_service_validate_url(ticket, service_url=service_url)
        logging.debug('[CAS] ServiceValidate URL: {}'.format(url))
        return self._perform_cas_call(url, ticket=ticket)

    def parse_logout_request(self, message_text):
        r'''Parse the contents of a CAS `LogoutRequest` XML message.'''
        result = {}
        xml_document = parseString(message_text)
        for node in xml_document.getElementsByTagName('saml:NameId'):
            for child in node.childNodes:
                if child.nodeType == child.TEXT_NODE:
                    result['name_id'] = child.nodeValue.strip()
        for node in xml_document.getElementsByTagName('samlp:SessionIndex'):
            for child in node.childNodes:
                if child.nodeType == child.TEXT_NODE:
                    result['session_index'] = child.nodeValue.strip()
        for key in xml_document.documentElement.attributes.keys():
            result[key] = xml_document.documentElement.getAttribute(key)
        logging.debug('[CAS] LogoutRequest:\n{}'.format(
            json.dumps(result, sort_keys=True, indent=4, separators=[',', ': ']),
            ))
        return result

    def create_session(self, ticket, payload=None, expires=None):
        r'''Create a session record from a service ticket.'''
        assert isinstance(self.session_storage_adapter, CASSessionAdapter)
        logging.debug('[CAS] Creating session for ticket {}'.format(ticket))
        self.session_storage_adapter.create(
            ticket,
            payload=payload,
            expires=expires,
            )

    def delete_session(self, ticket):
        r'''Delete a session record associated with a service ticket.'''
        assert isinstance(self.session_storage_adapter, CASSessionAdapter)
        logging.debug('[CAS] Deleting session for ticket {}'.format(ticket))
        self.session_storage_adapter.delete(ticket)

    def session_exists(self, ticket):
        r'''Test if a session records exists for a service ticket.'''
        assert isinstance(self.session_storage_adapter, CASSessionAdapter)
        exists = self.session_storage_adapter.exists(ticket)
        logging.debug('[CAS] Session [{}] exists: {}'.format(ticket, exists))
        return exists

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

    ### PUBLIC METHODS ###

    @property
    def auth_prefix(self):
        return self._auth_prefix

    @property
    def proxy_callback(self):
        return self._proxy_callback

    @property
    def proxy_url(self):
        return self._proxy_url

    @property
    def server_url(self):
        return self._server_url

    @property
    def service_url(self):
        return self._service_url

    @property
    def session_storage_adapter(self):
        return self._session_storage_adapter

    @property
    def verify_certificates(self):
        return self._verify_certificates


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
    def _parse_cas_xml_data(cls, xml_node, namespace='cas:'):
        result = {}
        tag_name = xml_node.nodeName
        if tag_name.startswith(namespace):
            tag_name = tag_name.replace(namespace, '')
        for child in xml_node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                text = child.nodeValue.strip()
                if text:
                    result[tag_name] = text
            elif child.nodeType == child.ELEMENT_NODE:
                subresult = cls._parse_cas_xml_data(child)
                result.setdefault(tag_name, {}).update(subresult)
        return result


class CASSessionAdapter(object):
    r'''An abstract session adapter.'''

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create(self, ticket, payload=None, expires=None):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, ticket):
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, ticket):
        raise NotImplementedError


class MemcachedCASSessionAdapter(CASSessionAdapter):
    r'''A Memcache session adapter.'''

    def __init__(self, memcached_client):
        self._memcached_client = memcached_client

    def create(self, ticket, payload=None, expires=None):
        if not payload:
            payload = True
        self.memcached_client.set(str(ticket), payload, expires)

    def delete(self, ticket):
        self.memcached_client.delete(str(ticket))

    def exists(self, ticket):
        return self.memcached_client.get(str(ticket)) is not None


__all__ = [
    'CASClient',
    'CASResponse',
    'CASSessionAdapter',
    'MemcachedCASSessionAdapter',
    ]
