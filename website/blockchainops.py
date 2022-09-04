from fileinput import filename
from eth_account import Account
import os
from solcx import compile_standard, install_solc
from web3 import Web3
from website.puf import getPUFResponse
from ecdsa import SECP256k1, SigningKey, VerifyingKey
import json


def getBCA():
    response = getPUFResponse()
    account = Account.from_key(response)
    return account.address


def returnABIByte():
    install_solc("0.8.15")

    with open(os.path.join(os.getcwd(), "PoC_smartNFT.sol"), "r") as file:
        contract = file.read()

    # print(contract)

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
        solc_version="0.8.15",
    )

    # print(compiled_sol)
    # print("Creating contract")
    # print(compiled_sol["contracts"]["PoC_smartNFT.sol"])

    bytecode = compiled_sol["contracts"]["PoC_smartNFT.sol"]["smartNFT_SC"]["evm"][
        "bytecode"
    ]["object"]

    # ABI
    abi = compiled_sol["contracts"]["PoC_smartNFT.sol"]["smartNFT_SC"]["abi"]
    return bytecode, abi


def deployBlockchain(fileName, password):
    # print(abi)
    bytecode, abi = returnABIByte()
    # For connecting to Ganache

    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    chain_id = 1337
    with open(
        os.path.join(os.getcwd(), "website", "keys", fileName + ".json"), "r"
    ) as file:
        ciphertext = file.read()

    acc = Account.from_key(Account.decrypt(ciphertext, password).hex())

    smartNFT = w3.eth.contract(abi=abi, bytecode=bytecode)
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


def createDeviceToken(ownerAddress, contractAddress, fileName, password):
    deviceAddress = getBCA()
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    chain_id = 1337
    with open(
        os.path.join(os.getcwd(), "website", "keys", fileName + ".json"), "r"
    ) as file:
        ciphertext = file.read()

    manufacturer = Account.from_key(Account.decrypt(ciphertext, password))
    print(manufacturer.address)

    _, abi = returnABIByte()

    smart_nft = w3.eth.contract(address=contractAddress, abi=abi)
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

    return send_store_tx, deviceAddress, publicKey.to_string("compressed").hex()
