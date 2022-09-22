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
    return "REDACTED_PRIVATE_KEY"
