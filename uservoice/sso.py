from Crypto.Cipher import AES
import base64
import hashlib
import datetime
import urllib
import pytz
import array
import operator
import simplejson as json

def generate_sso_token(subdomain_name, sso_key, user_attributes, valid_for = 300):
    current_time = (datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=valid_for)).strftime('%Y-%m-%d %H:%M:%S')
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

