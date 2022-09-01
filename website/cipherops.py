import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt
import os

def encrypt(sk,password,username):
    salt = get_random_bytes(16)
    key = scrypt(password, salt, 16, N=2**20, r=8, p=1)
    cipher = AES.new(key, AES.MODE_CTR)
    ct_bytes = cipher.encrypt(sk.encode())
    nonce = cipher.nonce.hex()
    ct = ct_bytes.hex()
    result = json.dumps({'nonce':nonce, 'sk':ct,'salt':salt.hex()})
    with open(os.path.join(os.getcwd(),'website', 'userdata', username + '.json'), 'w') as outfile:
        outfile.write(result)
        
def decrypt(password,username):
    f = open(os.path.join(os.getcwd(),'website', 'userdata', username + '.json'), "r")
    jsonString = json.loads(f.read())
    try:
        nonce = bytes.fromhex(jsonString["nonce"])
        ct = bytes.fromhex(jsonString["sk"])
        salt = bytes.fromhex(jsonString["salt"])
        key = scrypt(password, salt, 16, N=2**20, r=8, p=1)
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        pt = cipher.decrypt(ct)
        return pt.decode()
    except (ValueError, KeyError):
        return None
    