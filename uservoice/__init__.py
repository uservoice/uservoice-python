from Crypto.Cipher import AES
import base64
import hashlib
import urllib
import operator
import array
import simplejson as json
import urllib
import urllib2
import datetime
import pytz
from tweepy import oauth

def generate_sso_token(subdomain_name, sso_key, user_attributes):
    current_time = (datetime.datetime.now(pytz.utc) + datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    user_attributes.setdefault('expires', current_time)
    user_json = json.dumps(user_attributes, separators=(',',':'))
    iv = "OpenSSL for Ruby"
    block_size = 16

    salted = sso_key + subdomain_name
    saltedHash = hashlib.sha1(salted).digest()[:16]

    json_bytes = array.array('b', user_json[0 : len(user_json)])
    iv_bytes = array.array('b', iv[0 : len(iv)])

    for i in range(0, 16):
        json_bytes[i] = operator.xor(json_bytes[i], iv_bytes[i])

    pad = block_size - len(json_bytes.tostring()) % block_size
    data = json_bytes.tostring() + pad * chr(pad)
    aes = AES.new(saltedHash, AES.MODE_CBC, iv)
    encrypted_bytes = aes.encrypt(data)

    return urllib.quote(base64.b64encode(encrypted_bytes))

class OAuth:
    def __init__(self, subdomain_name, api_key, api_secret, callback=None):
        self.request_token = None
        self.access_token = None
        self.api_url = "https://" + subdomain_name + ".uservoice.com"
        self.consumer = oauth.OAuthConsumer(api_key, api_secret)
        self.callback = callback

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

