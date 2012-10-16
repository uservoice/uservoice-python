import operator
import array
import urllib
import urllib2
import simplejson as json
from tweepy import oauth

class APIError(RuntimeError): pass
class Unauthorized(APIError): pass
class NotFound(APIError): pass
class ApplicationError(APIError): pass

class Client:
    def __init__(self, subdomain_name, api_key, api_secret, callback=None, oauth_token='', oauth_token_secret=''):
        self.request_token = None
        self.token = oauth_token
        self.secret = oauth_token_secret
        self.access_token = oauth.OAuthToken(self.token, self.secret)
        self.default_headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' }
        self.api_url = "https://" + subdomain_name + ".uservoice.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.consumer = oauth.OAuthConsumer(api_key, api_secret)
        self.callback = callback
        self.subdomain_name = subdomain_name

    def get_request_token(self):
        url = self.api_url + '/oauth/request_token'
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, http_url=url, callback=self.callback
        )
        request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, None)
        resp = urllib2.urlopen(urllib2.Request(url, headers=request.to_header()))
        return oauth.OAuthToken.from_string(resp.read())

    def authorize_url(self):
        self.request_token = self.get_request_token()
        url = self.api_url + '/oauth/authorize'
        request = oauth.OAuthRequest.from_token_and_callback(
            token=self.request_token, http_url=url
        )
        return request.to_url()

    def get_access_token(self, verifier=None):
        url = self.api_url + '/oauth/access_token'

        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
            token=self.request_token, http_url=url,
            verifier=str(verifier)
        )
        request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, self.request_token)

        resp = urllib2.urlopen(urllib2.Request(url, headers=request.to_header()))
        self.access_token = oauth.OAuthToken.from_string(resp.read())
        return self.access_token

    def login_with_access_token(self, token, secret):
        return Client(self.subdomain_name, self.api_key, self.api_secret, callback=self.callback, oauth_token=token, oauth_token_secret=secret)

    def request(self, method, path, params={}):
        json_body = None
        if method.upper() in ['POST', 'PUT']:
            json_body = json.dumps(params)
        method = method.upper()
        url = self.api_url + path
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token,
            http_method=method, http_url=url, parameters={})
        request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, self.access_token)

        json_response = None
        try:
            attrs = json.load(urllib2.urlopen(urllib2.Request(url, json_body, dict(request.to_header().items() + self.default_headers.items()))))
            return attrs
        except urllib2.HTTPError as http_error:
            if http_error.code == 401:
                raise Unauthorized(http_error)
            elif http_error.code == 404:
                raise NotFound(http_error)
            elif http_error.code == 500:
                raise ApplicationError(http_error)
            else:
                raise APIError(http_error)


    # handy delegate methods
    def get(self, path, params={}): return self.request('get', path, params)
    def put(self, path, params={}): return self.request('put', path, params)
    def post(self, path, params={}): return self.request('post', path, params)
    def delete(self, path, params={}): return self.request('delete', path, params)

    def login_as(self, email):
        resp = self.post('/api/v1/users/login_as', {
            'request_token': self.get_request_token().key,
            'user': { 'email': email }
        })
        if resp['token']:
            token = resp['token']['oauth_token']
            secret = resp['token']['oauth_token_secret']
            return self.login_with_access_token(token, secret)

    def login_as_owner(self):
        resp = self.post('/api/v1/users/login_as_owner', {
            'request_token': self.get_request_token().key
        })
        if resp['token']:
            token = resp['token']['oauth_token']
            secret = resp['token']['oauth_token_secret']
            return self.login_with_access_token(token, secret)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass


