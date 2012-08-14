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
    def __init__(self, subdomain_name, api_key, api_secret):
        self.api_url = "https://" + subdomain_name + ".uservoice.com"
        self.consumer = oauth.OAuthConsumer(api_key, api_secret)

    def request(self, method, path, params={}):
        url = self.api_url + path
        request = oauth.OAuthRequest.from_consumer_and_token(
           self.consumer, http_method=method.upper(), http_url=url, parameters={})
        request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, None)

        headers = request.to_header()

        req = urllib2.Request(url, None, headers)

        return json.load(urllib2.urlopen(req))
