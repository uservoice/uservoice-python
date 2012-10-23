import operator
import array
import urllib
import urllib2
import simplejson as json
import uservoice
from oauth_hook import OAuthHook
from urlparse import parse_qs
import requests

class APIError(RuntimeError): pass
class Unauthorized(APIError): pass
class NotFound(APIError): pass
class ApplicationError(APIError): pass

class Client:
    def __init__(self, subdomain_name, api_key, api_secret, oauth_token='', oauth_token_secret='', callback=None):
        self.request_token = None
        self.token = oauth_token
        self.secret = oauth_token_secret
        self.default_headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' }
        self.access_token = requests.session(headers=self.default_headers, hooks={'pre_request': OAuthHook(self.token, self.secret, api_key, api_secret, True) })
        self.api_url = "https://" + subdomain_name + ".uservoice.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.callback = callback
        self.subdomain_name = subdomain_name

    def get_request_token(self, callback=None):
        url = self.api_url + '/oauth/request_token'
        body = {}
        if self.callback or callback:
            body['oauth_callback'] = self.callback or callback
        resp = requests.post(url, body, hooks={'pre_request': OAuthHook('', '', self.api_key, self.api_secret, True)})
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
        resp = requests.post(url, { 'oauth_verifier': verifier}, hooks={
            'pre_request': OAuthHook(self.request_token.token, self.request_token.secret, self.api_key, self.api_secret, True)})
        token = parse_qs(resp.text)
        return self.login_with_access_token(token['oauth_token'][0], token['oauth_token_secret'][0])

    def login_with_access_token(self, token, secret):
        return Client(self.subdomain_name, self.api_key, self.api_secret, oauth_token=token, oauth_token_secret=secret, callback=self.callback)

    def request(self, method, path, params={}):
        json_body = None
        get_parameters = {}
        method = method.upper()

        url = self.api_url + path
        json_resp = None
        if method == 'POST':
            json_resp = self.access_token.post(url, json.dumps(params))
        elif method == 'PUT':
            json_resp = self.access_token.put(url, json.dumps(params))
        elif method == 'GET':
            json_resp = self.access_token.get(url)
        elif method == 'DELETE':
            json_resp = self.access_token.delete(url)

        attrs = {}
        try:
            if json_resp.status_code == 404:
                attrs = {'errors': {'type': 'record_not_found' }}
            else:
                attrs = json.loads(json_resp.content)
        except json.JSONDecodeError as e:
            raise APIError(e)

        if 'errors' in attrs:
            if attrs['errors']['type'] == 'unauthorized':
                raise Unauthorized(attrs)
            elif attrs['errors']['type'] == 'record_not_found':
                raise NotFound(attrs)
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


