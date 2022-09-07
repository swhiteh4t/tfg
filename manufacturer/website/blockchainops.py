from fileinput import filename
from eth_account import Account
import os
from solcx import compile_standard, install_solc
from web3 import Web3
from website.cipherops import generateHashOfSharedSecret
from website.puf import getPUFResponse
from ecdsa import SECP256k1, SigningKey, VerifyingKey
import json
from abc import ABCMeta, abstractclassmethod, abstractstaticmethod


class BlockChainOps:

    __instance = None
    __w3 = None
    __abi = None
    __bytecode = None
    __version = "0.8.15"

    @staticmethod
    def getInstance():
        if BlockChainOps.__instance == None:
            BlockChainOps()
        return BlockChainOps.__instance

    @staticmethod
    def returnABIByte():
        install_solc(BlockChainOps.__version)

        with open(os.path.join(os.getcwd(), "ownable-iot.sol"), "r") as file:
            contract = file.read()

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

    def __init__(self):
        if BlockChainOps.__instance != None:
            pass
        else:
            BlockChainOps.__w3 = Web3(
                Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
            BlockChainOps.__abi, BlockChainOps.__bytecode = BlockChainOps.returnABIByte()
            BlockChainOps.__instance = self

    @staticmethod
    def getBCA():
        response = getPUFResponse()
        account = Account.from_key(response)
        return account.address

    @staticmethod
    def getDeviceState(addressDev, address):
        smart_nft = BlockChainOps.__w3.eth.contract(
            address=address, abi=BlockChainOps.__abi)
        tokenInfo = smart_nft.functions.getInfoTokenFromBCA(addressDev).call()
        dataEng = smart_nft.functions.getDataEngagement(addressDev).call()
        print(dataEng)
        if len(dataEng) != 0:
            hash = generateHashOfSharedSecret(dataEng)
            print(hash)
            print(dataEng)
            transaction = smart_nft.functions.ownerEngagement(hash).buildTransaction(
                {
                    "gasPrice": BlockChainOps.__w3.eth.gas_price,
                    "chainId": 1337,
                    "from": addressDev,
                    "nonce": BlockChainOps.__w3.eth.get_transaction_count(addressDev),
                }
            )
            signed_txn = BlockChainOps.__w3.eth.account.sign_transaction(
                transaction, private_key="0x" + getPUFResponse()
            )
            send_store_tx = BlockChainOps.__w3.eth.send_raw_transaction(
                signed_txn.rawTransaction)

        return "Engaged with owner" if tokenInfo[2] else "Waiting for owner"

    @staticmethod
    def deployBlockchain(fileName, password):
        # print(abi)
        # bytecode, abi = BlockChainOps.returnABIByte()
        # For connecting to Ganache

        chain_id = 1337
        with open(
            os.path.join(os.getcwd(), "website", "keys",
                         fileName + ".json"), "r"
        ) as file:
            ciphertext = file.read()

        acc = Account.from_key(Account.decrypt(ciphertext, password).hex())

        smartNFT = BlockChainOps.__w3.eth.contract(
            abi=BlockChainOps.__abi, bytecode=BlockChainOps.__bytecode)
        # Get lastest transaction count
        # print("Is connected-> " + str(w3.isConnected()))
        nonce = BlockChainOps.__w3.eth.get_transaction_count(acc.address)
        # 1 - Build a transaction
        # 2 - Sign the transaction
        # 3 - Send the transaction

        transaction = smartNFT.constructor().buildTransaction(
            {
                "gasPrice": BlockChainOps.__w3.eth.gas_price,
                "chainId": chain_id,
                "from": acc.address,
                "nonce": nonce,
            }
        )
        signed_transaction = BlockChainOps.__w3.eth.account.sign_transaction(
            transaction, private_key=acc.key
        )
        tx_hash = BlockChainOps.__w3.eth.send_raw_transaction(
            signed_transaction.rawTransaction)
        tx_receipt = BlockChainOps.__w3.eth.wait_for_transaction_receipt(
            tx_hash)

        return tx_receipt.contractAddress

    @staticmethod
    def createDeviceToken(ownerAddress, contractAddress, fileName, password):
        deviceAddress = BlockChainOps.getBCA()

        chain_id = 1337
        with open(
            os.path.join(os.getcwd(), "website", "keys",
                         fileName + ".json"), "r"
        ) as file:
            ciphertext = file.read()

        manufacturer = Account.from_key(Account.decrypt(ciphertext, password))
        # print(manufacturer.address)

        smart_nft = BlockChainOps.__w3.eth.contract(
            address=contractAddress, abi=BlockChainOps.__abi
        )

        if smart_nft.functions.tokenFromBCA(deviceAddress).call() == 0:
            # print("Contract address -> " + contractAddress)
            # Call -> Simulate making the call and getting a return value (blue buttons)
            # Transact -> Actually making a state change in the block chain (orange buttongs)
            store_transaction = smart_nft.functions.createToken(
                deviceAddress, ownerAddress
            ).build_transaction(
                {
                    "gasPrice": BlockChainOps.__w3.eth.gas_price,
                    "chainId": chain_id,
                    "from": manufacturer.address,
                    "nonce": BlockChainOps.__w3.eth.get_transaction_count(manufacturer.address),
                }
            )

            sk_dev = SigningKey.from_string(
                bytearray.fromhex(getPUFResponse()), curve=SECP256k1
            )
            publicKey = sk_dev.verifying_key

            signed_txn = BlockChainOps.__w3.eth.account.sign_transaction(
                store_transaction, private_key=manufacturer.key
            )
            send_store_tx = BlockChainOps.__w3.eth.send_raw_transaction(
                signed_txn.rawTransaction)

            # print(send_store_tx)
        else:
            return None, None, None
        return deviceAddress, publicKey.to_string("compressed").hex()
