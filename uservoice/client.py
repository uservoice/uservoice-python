from future import standard_library
standard_library.install_aliases()
from builtins import object
import operator
import array
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json
import uservoice
from requests_oauthlib import OAuth1
from urllib.parse import parse_qs
import requests
version='0.0.23'

class APIError(RuntimeError): pass
class Unauthorized(APIError): pass
class NotFound(APIError): pass
class RateLimitExceeded(APIError): pass
class ApplicationError(APIError): pass

class Client(object):
    def __init__(self, subdomain_name, api_key, api_secret=None, oauth_token='', oauth_token_secret='', callback=None, protocol=None, uservoice_domain=None):
        self.request_token = None
        self.token = oauth_token
        self.secret = oauth_token_secret
        self.default_headers = { 'Content-Type': 'application/json', 'Accept': 'application/json',  'API-Client': 'uservoice-python-' + version }
        oauth_hooks = {}
        if api_secret:
            self.oauth = OAuth1(api_key, api_secret, resource_owner_key=self.token, resource_owner_secret=self.secret, callback_uri=callback)
        else:
            self.oauth = None
        self.api_url = "{protocol}://{subdomain_name}.{uservoice_domain}".format(
                           subdomain_name=subdomain_name,
                           protocol=(protocol or 'https'),
                           uservoice_domain=(uservoice_domain or 'uservoice.com')
                       )
        self.api_key = api_key
        self.api_secret = api_secret
        self.callback = callback
        self.subdomain_name = subdomain_name
        self.uservoice_domain = uservoice_domain
        self.protocol = protocol

    def get_request_token(self, callback=None):
        url = self.api_url + '/oauth/request_token'
        body = {}
        if self.callback or callback:
            body['oauth_callback'] = callback or self.callback
        oauth = OAuth1(self.api_key, self.api_secret, callback_uri=self.callback)
        resp = requests.post(url, body, headers=self.default_headers, auth=oauth)
        token = parse_qs(resp.text)
        if not 'oauth_token' in token or not 'oauth_token_secret' in token:
            raise Unauthorized('Failed to get request token')
        return self.login_with_access_token(token['oauth_token'][0], token['oauth_token_secret'][0])

    def authorize_url(self):
        self.request_token = self.get_request_token()
        url = self.api_url + '/oauth/authorize?oauth_token=' + self.request_token.token
        return url

    def login_with_verifier(self, verifier=None):
        url = self.api_url + '/oauth/access_token'
        oauth = OAuth1(self.api_key, self.api_secret, resource_owner_key=self.request_token.token, resource_owner_secret=self.request_token.secret, callback_uri=self.callback, verifier=verifier)
        resp = requests.post(url, auth=oauth)
        token = parse_qs(resp.text)
        return self.login_with_access_token(token['oauth_token'][0], token['oauth_token_secret'][0])

    def login_with_access_token(self, token, secret):
        return Client(self.subdomain_name, self.api_key, self.api_secret, oauth_token=token, oauth_token_secret=secret, callback=self.callback,
                                                                                                                        protocol=self.protocol,
                                                                                                                        uservoice_domain=self.uservoice_domain)

    def request(self, method, path, params={}):
        json_body = None
        get_parameters = {}
        method = method.upper()

        url = self.api_url + path
        if self.api_secret == None:
            if '?' in url:
                url += '&client=' + self.api_key
            else:
                url += '?client=' + self.api_key
        json_resp = None
        if method == 'POST':
            json_resp = requests.post(url, json.dumps(params), headers=self.default_headers, auth=self.oauth)
        elif method == 'PUT':
            json_resp = requests.put(url, json.dumps(params), headers=self.default_headers, auth=self.oauth)
        elif method == 'GET':
            json_resp = requests.get(url, headers=self.default_headers, auth=self.oauth)
        elif method == 'DELETE':
            json_resp = requests.delete(url, headers=self.default_headers, auth=self.oauth)

        attrs = {}
        try:
            if json_resp.status_code == 404:
                attrs = {'errors': {'type': 'record_not_found' }}
            elif json_resp.status_code == 429:
                attrs = {'errors': {'type': 'rate_limit_exceeded' }}
            else:
                attrs = json_resp.json()
        except json.JSONDecodeError as e:
            raise APIError(e)

        if 'errors' in attrs:
            if attrs['errors']['type'] == 'unauthorized':
                raise Unauthorized(attrs)
            elif attrs['errors']['type'] == 'record_not_found':
                raise NotFound(attrs)
            elif attrs['errors']['type'] == 'rate_limit_exceeded':
                raise RateLimitExceeded(attrs)
            elif attrs['errors']['type'] == 'application_error':
                raise ApplicationError(attrs)
            else:
                raise APIError(attrs)
        return attrs


    # handy delegate methods
    def get(self, path, params={}): return self.request('get', path, params)
    def put(self, path, params={}): return self.request('put', path, params)
    def post(self, path, params={}): return self.request('post', path, params)
    def delete(self, path, params={}): return self.request('delete', path, params)

    def get_collection(self, path, **opts):
        return uservoice.Collection(self, path, **opts)

    def login_as(self, email):
        resp = self.post('/api/v1/users/login_as', {
            'request_token': self.get_request_token().token,
            'user': { 'email': email }
        })
        if 'token' in resp:
            token = resp['token']['oauth_token']
            secret = resp['token']['oauth_token_secret']
            return self.login_with_access_token(token, secret)
        else:
            raise Unauthorized(resp)

    def login_as_owner(self):
        resp = self.post('/api/v1/users/login_as_owner', {
            'request_token': self.get_request_token().token
        })
        if 'token' in resp:
            token = resp['token']['oauth_token']
            secret = resp['token']['oauth_token_secret']
            return self.login_with_access_token(token, secret)
        else:
            raise Unauthorized(resp)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
