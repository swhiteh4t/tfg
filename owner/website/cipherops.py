from ecdsa import ECDH, SECP256k1, SigningKey, VerifyingKey
from hashlib import sha256


def generatePublicKeyandDataEng(priv, remote_public_key):
    private = SigningKey.from_string(priv, curve=SECP256k1)
    ecdh = ECDH(curve=SECP256k1, private_key=private,
                public_key=private.get_verifying_key())
    ecdh.load_received_public_key_bytes(bytearray.fromhex(
        remote_public_key), valid_encodings="compressed")
    return private.get_verifying_key().to_string("compressed").hex(), ecdh.generate_sharedsecret_bytes()


def generateHashOfSharedSecret(secret):
    return int(sha256(secret).hexdigest(), 16)
