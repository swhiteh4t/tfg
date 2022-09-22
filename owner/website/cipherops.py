from ecdsa import ECDH, SECP256k1, SigningKey, VerifyingKey
from hashlib import sha256
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
import json
from base64 import b64encode
from Crypto.Random import get_random_bytes
from eth_account import Account

from website.io import readKey


def generatePublicKeyandDataEng(priv, remote_public_key):
    private = SigningKey.from_string(priv, curve=SECP256k1)
    ecdh = ECDH(curve=SECP256k1, private_key=private,
                public_key=private.get_verifying_key())
    ecdh.load_received_public_key_bytes(bytearray.fromhex(
        remote_public_key), valid_encodings="compressed")
    return private.get_verifying_key().to_string("compressed").hex(), ecdh.generate_sharedsecret_bytes()


def getPublic(password):
    ciphertext = readKey("owner")
    owner = Account.from_key(Account.decrypt(ciphertext, password).hex())
    private = SigningKey.from_string(owner.key, curve=SECP256k1)
    return private.get_verifying_key().to_string("compressed").hex()


def generateHashOfSharedSecret(secret):
    return int(sha256(secret).hexdigest(), 16)


def encrypt(key, plaintext, token=True):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    result = json.dumps({'iv': iv, 'ciphertext': ct})
    return result


def decrypt(key, ciphertext, token=True):
    try:
        b64 = json.loads(ciphertext)
        iv = b64decode(b64['iv'])
        ct = b64decode(b64['ciphertext'])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt
    except (ValueError, KeyError):
        print("Incorrect decryption")
