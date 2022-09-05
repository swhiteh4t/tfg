from solcx import compile_standard
from web3 import Web3

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "SimpleStorage.sol": {"content": simple_storage_file},
        },
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evn.sourceMap"]}
            }
        },
    },
    solc_version="0.8.15",
)

w3 = Web3(
    Web3.HTTPProvider("http://127.0.0.1:7545")
)

