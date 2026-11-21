import os
from pypuf.simulation import XORBistableRingPUF
from numpy.random import default_rng
from pypuf.io import random_inputs


def converToBin(a):
    binaryString = ""
    for digit in a:
        if digit < 0:
            binaryString += "0"
        else:
            binaryString += "1"
    return binaryString


def converToHex(a):
    binaryString = ""
    for digit in a:
        if digit < 0:
            binaryString += "0"
        else:
            binaryString += "1"
    return hex(int(binaryString, 2))


SEED = 25

# Get the account from the challenge-response PUF


def getPUFResponse():
    k, n = 8, 64
    weights = default_rng(1).normal(size=(k, n + 1))
    puf = XORBistableRingPUF(n=64, k=8, weights=weights)
    response = puf.eval(random_inputs(n=64, N=256, seed=SEED))
    # The PUF is simulated: the device key is read from the environment instead
    # of being derived from `response`. Use a local Ganache account key.
    key = os.environ.get("DEVICE_PRIVATE_KEY")
    if not key:
        raise RuntimeError("Set DEVICE_PRIVATE_KEY (hex, without 0x) to the device's Ganache private key")
    return key.removeprefix("0x")
