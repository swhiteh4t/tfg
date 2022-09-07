from fileinput import filename
from eth_account import Account
from solcx import compile_standard, install_solc
from web3 import Web3
from ecdsa import SECP256k1, SigningKey, VerifyingKey
import os
import website.cipherops

from website.io import readContract, readContractAddress, readKey


class BlockChainOps:

    __instance = None
    __w3 = None
    __abi = None
    __bytecode = None
    __version = "0.8.15"
    __chainID = 1337

    @staticmethod
    def getInstance():
        if BlockChainOps.__instance == None:
            BlockChainOps()
        return BlockChainOps.__instance

    @staticmethod
    def returnABIByte():
        install_solc(BlockChainOps.__version)

        contract = readContract()

        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {
                    "ownable-iot.sol": {"content": contract},
                },
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "metadata", "evm.bytecode", "evn.sourceMap"]}
                    }
                },
            },
            solc_version=BlockChainOps.__version,
        )
        bytecode = compiled_sol["contracts"]["ownable-iot.sol"]["OwnableIoT"]["evm"][
            "bytecode"
        ]["object"]

        # ABI
        abi = compiled_sol["contracts"]["ownable-iot.sol"]["OwnableIoT"]["abi"]
        return abi, bytecode

    @staticmethod
    def setWebProvider(url):
        __w3 = Web3(Web3.HTTPProvider(url))

    @staticmethod
    def setSolidityVersion(version):
        __version = version

    # Constructor function
    def __init__(self):
        if BlockChainOps.__instance != None:
            pass
        else:
            BlockChainOps.__w3 = Web3(
                Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
            BlockChainOps.__abi, BlockChainOps.__bytecode = BlockChainOps.returnABIByte()
            BlockChainOps.__instance = self

    @staticmethod
    def getDeviceState(addressDev, address):
        smart_nft = BlockChainOps.__w3.eth.contract(
            address=address, abi=BlockChainOps.__abi)
        tokenInfo = smart_nft.functions.getInfoTokenFromBCA(addressDev).call()
        return "Engaged with owner" if tokenInfo[2] else "Waiting for owner"

    @staticmethod
    def engageDevice(fileName, password, public, devAddress):
        ciphertext = readKey(fileName)

        contractAddress = readContractAddress()

        owner = Account.from_key(Account.decrypt(ciphertext, password).hex())

        smart_nft = BlockChainOps.__w3.eth.contract(
            address=contractAddress, abi=BlockChainOps.__abi
        )

        tokenId = smart_nft.functions.tokenFromBCA(devAddress).call()

        dataEngagement, secret = website.cipherops.generatePublicKeyandDataEng(
            owner.key, public)

        hash = website.cipherops.generateHashOfSharedSecret(secret)
        print(hash)
        transaction = smart_nft.functions.startOwnerEngagement(tokenId, dataEngagement, hash).build_transaction(
            {
                "gasPrice": BlockChainOps.__w3.eth.gas_price,
                "chainId": BlockChainOps.__chainID,
                "from": owner.address,
                "nonce": BlockChainOps.__w3.eth.get_transaction_count(owner.address),
            }
        )

        signed_txn = BlockChainOps.__w3.eth.account.sign_transaction(
            transaction, private_key=owner.key
        )
        send_store_tx = BlockChainOps.__w3.eth.send_raw_transaction(
            signed_txn.rawTransaction)
        print(smart_nft.functions.getInfoTokenFromBCA(devAddress).call())
        return smart_nft.functions.getInfoTokenFromBCA(devAddress).call()

    @staticmethod
    def getSecret(fileName, password, public):
        ciphertext = readKey(fileName)

        contractAddress = readContractAddress()

        owner = Account.from_key(Account.decrypt(ciphertext, password).hex())
        dataEngagement, secret = website.cipherops.generatePublicKeyandDataEng(
            owner.key, public)
        return secret

    @staticmethod
    def setCertificateToken(fileName, password, token, addressSD):
        ciphertext = readKey(fileName)

        contractAddress = readContractAddress()

        owner = Account.from_key(Account.decrypt(ciphertext, password).hex())

        smart_nft = BlockChainOps.__w3.eth.contract(
            address=contractAddress, abi=BlockChainOps.__abi
        )

        transaction = smart_nft.functions.setTokenStorage(addressSD, token).build_transaction(
            {
                "gasPrice": BlockChainOps.__w3.eth.gas_price,
                "chainId": BlockChainOps.__chainID,
                "from": owner.address,
                "nonce": BlockChainOps.__w3.eth.get_transaction_count(owner.address),
            }
        )

        signed_txn = BlockChainOps.__w3.eth.account.sign_transaction(
            transaction, private_key=owner.key
        )
        send_store_tx = BlockChainOps.__w3.eth.send_raw_transaction(
            signed_txn.rawTransaction)

    @staticmethod
    def setCertificateHash(fileName, password, token, addressSD):
        ciphertext = readKey(fileName)

        contractAddress = readContractAddress()

        owner = Account.from_key(Account.decrypt(ciphertext, password).hex())

        smart_nft = BlockChainOps.__w3.eth.contract(
            address=contractAddress, abi=BlockChainOps.__abi
        )

        transaction = smart_nft.functions.setCertificateDigest(addressSD, token).build_transaction(
            {
                "gasPrice": BlockChainOps.__w3.eth.gas_price,
                "chainId": BlockChainOps.__chainID,
                "from": owner.address,
                "nonce": BlockChainOps.__w3.eth.get_transaction_count(owner.address),
            }
        )

        signed_txn = BlockChainOps.__w3.eth.account.sign_transaction(
            transaction, private_key=owner.key
        )
        send_store_tx = BlockChainOps.__w3.eth.send_raw_transaction(
            signed_txn.rawTransaction)
