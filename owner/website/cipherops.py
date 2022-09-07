from ecdsa import ECDH, SECP256k1, SigningKey, VerifyingKey
from hashlib import sha256
from Crypto.Cipher import AES


def generatePublicKeyandDataEng(priv, remote_public_key):
    private = SigningKey.from_string(priv, curve=SECP256k1)
    ecdh = ECDH(curve=SECP256k1, private_key=private,
                public_key=private.get_verifying_key())
    ecdh.load_received_public_key_bytes(bytearray.fromhex(
        remote_public_key), valid_encodings="compressed")
    return private.get_verifying_key().to_string("compressed").hex(), ecdh.generate_sharedsecret_bytes()


def generateHashOfSharedSecret(secret):
    return int(sha256(secret).hexdigest(), 16)


def encrypt(key, plaintext):
    nonce = sha256(key).digest()[0:15]
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    ct_bytes = cipher.encrypt(plaintext.encode())
    return ct_bytes.hex()


def decrypt(key, ciphertext):
    nonce = sha256(key.encode()).digest()[0:15]
    try:
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        return cipher.decrypt(ciphertext)
    except (ValueError, KeyError):
        return None
