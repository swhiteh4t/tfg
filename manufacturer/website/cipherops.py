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


def encrypt(sk, password, username):
    salt = get_random_bytes(16)
    key = scrypt(password, salt, 16, N=2**20, r=8, p=1)
    cipher = AES.new(key, AES.MODE_CTR)
    ct_bytes = cipher.encrypt(sk.encode())
    nonce = cipher.nonce.hex()
    ct = ct_bytes.hex()
    result = json.dumps({"nonce": nonce, "sk": ct, "salt": salt.hex()})
    with open(
        os.path.join(os.getcwd(), "website", "userdata",
                     username + ".json"), "w"
    ) as outfile:
        outfile.write(result)


def decrypt(password, username):
    f = open(os.path.join(os.getcwd(), "website",
             "userdata", username + ".json"), "r")
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
