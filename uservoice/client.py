import operator
import array
import urllib
import urllib2
from tweepy import oauth
from sso import generate_sso_token

class Client:
    def __init__(self, subdomain_name, api_key, api_secret, callback=None, sso_key=None):
        self.request_token = None
        self.access_token = None
        self.api_url = "https://" + subdomain_name + ".uservoice.com"
        self.consumer = oauth.OAuthConsumer(api_key, api_secret)
        self.callback = callback
        self.sso_key = sso_key
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

    def request(self, method, path, params={}):
        url = self.api_url + path
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, 
            token=self.access_token,
            http_method=method.upper(), http_url=url, parameters={})
        request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, self.access_token)

        return urllib2.urlopen(urllib2.Request(url, None, request.to_header()))

    def login_as(self, email):
        generate_sso_token('','','')
        return 0


