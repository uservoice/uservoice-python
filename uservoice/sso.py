from future import standard_library
standard_library.install_aliases()
from builtins import chr
from builtins import range
from Crypto.Cipher import AES
import base64
import hashlib
import datetime
import urllib.request, urllib.parse, urllib.error
import pytz
import array
import operator
import json
import sys

def generate_sso_token(subdomain_name, sso_key, user_attributes, valid_for = 300):
    current_time = (datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=valid_for)).strftime('%Y-%m-%d %H:%M:%S')
    user_attributes.setdefault('expires', current_time)
    user_json = json.dumps(user_attributes, separators=(',',':'))
    iv = "OpenSSL for Ruby"
    block_size = 16

    salted = sso_key + subdomain_name
    saltedHash = hashlib.sha1(salted.encode('utf8')).digest()[:16]

    json_bytes = array.array('b', user_json.encode('utf8'))
    iv_bytes = array.array('b', iv.encode('utf8'))

    for i in range(0, 16):
        json_bytes[i] = operator.xor(json_bytes[i], iv_bytes[i])

    pad = block_size - len(json_bytes) % block_size
    data = json_bytes + array.array('b', [pad] * pad)
    aes = AES.new(saltedHash, AES.MODE_CBC, iv)
    if sys.version_info[0] < 3:
        data_bytes = data.tostring()
    else:
        data_bytes = data.tobytes()
    encrypted_bytes = aes.encrypt(data_bytes)

    return urllib.parse.quote(base64.b64encode(encrypted_bytes))

