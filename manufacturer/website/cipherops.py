import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt
import os
from ecdsa import ECDH, SECP256k1, SigningKey, VerifyingKey
from hashlib import sha256
from Crypto.Util.Padding import unpad, pad

# Generate the shared secret
from ecdsa import ECDH, SECP256k1

from website.puf import getPUFResponse


from ecdsa import ECDH, SECP256k1, SigningKey, VerifyingKey
from hashlib import sha256
from Crypto.Cipher import AES


def generatePublicKeyandDataEng(remote_public_key):
    private = SigningKey.from_string(
        bytearray.fromhex(getPUFResponse()), curve=SECP256k1)
    ecdh = ECDH(curve=SECP256k1, private_key=private,
                public_key=private.get_verifying_key())
    ecdh.load_received_public_key_bytes(bytearray.fromhex(
        remote_public_key), valid_encodings="compressed")
    return private.get_verifying_key().to_string("compressed").hex(), ecdh.generate_sharedsecret_bytes()


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


def generateHashOfSharedSecret(remote_public_key):
    priv = getPUFResponse()
    private = SigningKey.from_string(bytearray.fromhex(priv), curve=SECP256k1)
    ecdh = ECDH(curve=SECP256k1, private_key=private,
                public_key=private.get_verifying_key())
    print(remote_public_key)
    ecdh.load_received_public_key_bytes(bytearray.fromhex(
        remote_public_key), valid_encodings="compressed")
    secret = ecdh.generate_sharedsecret_bytes()
    return int(sha256(secret).hexdigest(), 16)
