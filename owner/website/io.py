import json
import os


def readContract():
    with open(os.path.join(os.getcwd(), "ownable-iot.sol"), "r") as file:
        contract = file.read()
    file.close()
    return contract


def readKey(fileName):
    with open(
        os.path.join(os.getcwd(), "website", "keys",
                     fileName + ".json"), "r"
    ) as file:
        ciphertext = file.read()
    file.close()
    return ciphertext


def readContractAddress():
    with open(
        os.path.join(os.getcwd(), "website", "contract",
                     "contract" + ".address"), "r"
    ) as file:
        contractAddress = file.read()
    file.close()
    return contractAddress


def writeContractAddress(contract):
    with open(os.path.join(os.getcwd(), "website", "contract", "contract.address"), "w") as file:
        file.write(contract)
    file.close()


def readPowerGateConfig():
    with open(os.path.join(os.getcwd(), "website", "powergate", "default.json"), "r") as f:
        result = f.read()
    return json.loads(result)
