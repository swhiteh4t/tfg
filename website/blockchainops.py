from fileinput import filename
from eth_account import Account
import os
from solcx import compile_standard, install_solc
from web3 import Web3
from website.puf import getPUFResponse
from ecdsa import SECP256k1, SigningKey, VerifyingKey
import json
from abc import ABCMeta, abstractclassmethod, abstractstaticmethod


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

        with open(os.path.join(os.getcwd(), "PoC_smartNFT.sol"), "r") as file:
            contract = file.read()

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

    def __init__(self):
        if CipherOps.__instance != None:
            pass
        else:
            CipherOps.__w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
            CipherOps.__abi, CipherOps.__bytecode = CipherOps.returnABIByte()
            CipherOps.__instance = self

    @staticmethod
    def getBCA():
        response = getPUFResponse()
        account = Account.from_key(response)
        return account.address

    @staticmethod
    def getDeviceState(addressDev, address):
        smart_nft = CipherOps.__w3.eth.contract(address=address, abi=CipherOps.__abi)
        tokenInfo = smart_nft.functions.getInfoTokenFromBCA(addressDev).call()
        return "Engaged with owner" if tokenInfo[2] else "Waiting for owner"

    @staticmethod
    def deployBlockchain(fileName, password):
        # print(abi)
        # bytecode, abi = CipherOps.returnABIByte()
        # For connecting to Ganache

        w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
        chain_id = 1337
        with open(
            os.path.join(os.getcwd(), "website", "keys", fileName + ".json"), "r"
        ) as file:
            ciphertext = file.read()

        acc = Account.from_key(Account.decrypt(ciphertext, password).hex())

        smartNFT = w3.eth.contract(abi=CipherOps.__abi, bytecode=CipherOps.__bytecode)
        # Get lastest transaction count
        # print("Is connected-> " + str(w3.isConnected()))
        nonce = w3.eth.get_transaction_count(acc.address)
        # 1 - Build a transaction
        # 2 - Sign the transaction
        # 3 - Send the transaction

        transaction = smartNFT.constructor().buildTransaction(
            {
                "gasPrice": w3.eth.gas_price,
                "chainId": chain_id,
                "from": acc.address,
                "nonce": nonce,
            }
        )
        signed_transaction = w3.eth.account.sign_transaction(
            transaction, private_key=acc.key
        )
        tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_receipt.contractAddress

    @staticmethod
    def createDeviceToken(ownerAddress, contractAddress, fileName, password):
        deviceAddress = CipherOps.getBCA()
        w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
        chain_id = 1337
        with open(
            os.path.join(os.getcwd(), "website", "keys", fileName + ".json"), "r"
        ) as file:
            ciphertext = file.read()

        manufacturer = Account.from_key(Account.decrypt(ciphertext, password))
        print(manufacturer.address)

        smart_nft = CipherOps.__w3.eth.contract(
            address=contractAddress, abi=CipherOps.__abi
        )

        if smart_nft.functions.tokenFromBCA(deviceAddress).call() == 0:
            # print("Contract address -> " + contractAddress)
            # Call -> Simulate making the call and getting a return value (blue buttons)
            # Transact -> Actually making a state change in the block chain (orange buttongs)
            store_transaction = smart_nft.functions.createToken(
                deviceAddress, ownerAddress
            ).build_transaction(
                {
                    "gasPrice": w3.eth.gas_price,
                    "chainId": chain_id,
                    "from": manufacturer.address,
                    "nonce": w3.eth.get_transaction_count(manufacturer.address),
                }
            )

            sk_dev = SigningKey.from_string(
                bytearray.fromhex(getPUFResponse()), curve=SECP256k1
            )
            publicKey = sk_dev.verifying_key

            signed_txn = w3.eth.account.sign_transaction(
                store_transaction, private_key=manufacturer.key
            )
            send_store_tx = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # print(send_store_tx)
        else:
            return None, None, None
        return deviceAddress, publicKey.to_string("compressed").hex()
