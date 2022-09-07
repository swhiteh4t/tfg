import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt
import os
from ecdsa import ECDH, SECP256k1, SigningKey, VerifyingKey
from hashlib import sha256


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


def encrypt(key, plaintext):
    nonce = sha256(key).digest()[0:15]
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    ct_bytes = cipher.encrypt(plaintext.encode())
    return ct_bytes.hex()


def decrypt(key, ciphertext):
    nonce = sha256(key).digest()[0:15]
    try:
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        return cipher.decrypt(bytes.fromhex(ciphertext))
    except (ValueError, KeyError):
        return None


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
