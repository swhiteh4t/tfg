from fileinput import filename
from eth_account import Account
from solcx import compile_standard, install_solc
from web3 import Web3
from ecdsa import SECP256k1, SigningKey, VerifyingKey
import os
from abc import ABCMeta, abstractclassmethod, abstractstaticmethod
from website.cipherops import generateHashOfSharedSecret, generatePublicKeyandDataEng

from website.io import readContract, readContractAddress, readKey


class CipherOps:

    __instance = None
    __w3 = None
    __abi = None
    __bytecode = None
    __version = "0.8.15"

    @staticmethod
    def getInstance():
        if CipherOps.__instance == None:
            CipherOps()
        return CipherOps.__instance

    @staticmethod
    def returnABIByte():
        install_solc(CipherOps.__version)

        contract = readContract()

        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {
                    "PoC_smartNFT.sol": {"content": contract},
                },
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "metadata", "evm.bytecode", "evn.sourceMap"]}
                    }
                },
            },
            solc_version=CipherOps.__version,
        )
        bytecode = compiled_sol["contracts"]["PoC_smartNFT.sol"]["smartNFT_SC"]["evm"][
            "bytecode"
        ]["object"]

        # ABI
        abi = compiled_sol["contracts"]["PoC_smartNFT.sol"]["smartNFT_SC"]["abi"]
        return abi, bytecode

    @staticmethod
    def setWebProvider(url):
        __w3 = Web3(Web3.HTTPProvider(url))

    @staticmethod
    def setSolidityVersion(version):
        __version = version

    # Constructor function
    def __init__(self):
        if CipherOps.__instance != None:
            pass
        else:
            CipherOps.__w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
            CipherOps.__abi, CipherOps.__bytecode = CipherOps.returnABIByte()
            CipherOps.__instance = self

    @staticmethod
    def getDeviceState(addressDev, address):
        smart_nft = CipherOps.__w3.eth.contract(
            address=address, abi=CipherOps.__abi)
        tokenInfo = smart_nft.functions.getInfoTokenFromBCA(addressDev).call()
        return "Engaged with owner" if tokenInfo[2] else "Waiting for owner"

    @staticmethod
    def engageDevice(fileName, password, public, devAddress):
        chain_id = 1337

        ciphertext = readKey(fileName)

        contractAddress = readContractAddress()

        owner = Account.from_key(Account.decrypt(ciphertext, password).hex())

        smart_nft = CipherOps.__w3.eth.contract(
            address=contractAddress, abi=CipherOps.__abi
        )

        tokenId = smart_nft.functions.tokenFromBCA(devAddress).call()

        dataEngagement, secret = generatePublicKeyandDataEng(owner.key, public)

        hash = generateHashOfSharedSecret(secret)
        print(hash)
        transaction = smart_nft.functions.startOwnerEngagement(tokenId, dataEngagement, hash).build_transaction(
            {
                "gasPrice": CipherOps.__w3.eth.gas_price,
                "chainId": chain_id,
                "from": owner.address,
                "nonce": CipherOps.__w3.eth.get_transaction_count(owner.address),
            }
        )

        signed_txn = CipherOps.__w3.eth.account.sign_transaction(
            transaction, private_key=owner.key
        )
        send_store_tx = CipherOps.__w3.eth.send_raw_transaction(
            signed_txn.rawTransaction)
        print(smart_nft.functions.getInfoTokenFromBCA(devAddress).call())
        return smart_nft.functions.getInfoTokenFromBCA(devAddress).call()
