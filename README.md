# Ownable IoT — Blockchain-based ownership of IoT devices

Final degree project (TFG). A proof of concept for managing ownership of IoT devices with
**smart NFTs** on Ethereum. Each device is bound to an ERC-721 token, its identity is
derived from a (simulated) **PUF**, and device/owner keys are agreed with **ECDH (secp256k1)**.
Device certificates are stored off-chain on **IPFS/Filecoin via Powergate**.

The project has two Flask web apps, one for each actor:

| App            | Port | What it does                                                                             |
|----------------|------|------------------------------------------------------------------------------------------|
| `manufacturer` | 4040 | Deploy the `OwnableIoT` contract, register devices (mint tokens), list contracts/devices, get device certificates |
| `owner`        | 5000 | Get the owner public key, engage with a device, register devices, create and list certificates |

## Repository layout

```
manufacturer/
├── main.py                   # Flask entry point (port 4040)
├── ownable-iot.sol           # OwnableIoT smart contract (ERC-721 + smartNFT)
├── ERC721_Interface.sol
├── SmartNFT_Interface.sol
└── website/
    ├── blockchainops.py      # web3 / contract interaction
    ├── cipherops.py          # ECDH + AES helpers
    ├── puf.py                # simulated PUF (pypuf)
    ├── powergateops.py       # IPFS/Filecoin storage via Powergate
    ├── contracts/            # ABIs of deployed contracts
    ├── keys/                 # encrypted Ethereum keystores (not committed)
    ├── certificates/         # generated certificates (not committed)
    └── templates/, static/
owner/                        # same structure for the owner side
```

## Requirements

- Python 3.9+
- [Ganache](https://trufflesuite.com/ganache/) running at `http://127.0.0.1:7545`
- A [Powergate](https://github.com/textileio/powergate) node
- Python packages:

```bash
pip install flask flask-sqlalchemy flask-login bcrypt web3 py-solc-x \
            ecdsa pycryptodome pyopenssl pypuf numpy pygate-grpc
```

`py-solc-x` downloads the Solidity compiler (`^0.8.15`) on first run.

## Setup

1. Start Ganache on port 7545.
2. Create an encrypted keystore for each actor from a Ganache account and put it in:
   - `manufacturer/website/keys/<name>.json`
   - `owner/website/keys/<name>.json`

   For example:
   ```python
   import json
   from eth_account import Account
   ks = Account.encrypt("<ganache-private-key>", "<password>")
   json.dump(ks, open("website/keys/manufacturer.json", "w"))
   ```
3. Check the Powergate settings in `website/powergate/default.json`.
4. Set the environment variables:

   | Variable             | Used by      | Description                                                       |
   |----------------------|--------------|-------------------------------------------------------------------|
   | `SECRET_KEY`         | both apps    | Flask session key. If unset, a random one is made on each start (sessions end on restart). |
   | `POWERGATE_HOST`     | both apps    | Powergate address, `host:port`. Default `127.0.0.1:5002`.          |
   | `DEVICE_PRIVATE_KEY` | manufacturer | Private key (hex) of the Ganache account the simulated PUF device uses. |

   ```bash
   export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
   export POWERGATE_HOST="127.0.0.1:5002"
   export DEVICE_PRIVATE_KEY="<ganache-private-key>"
   ```

## Running

Start each app **from its own folder**, because paths are relative to the working directory:

```bash
cd manufacturer && python main.py   # http://localhost:4040
cd owner        && python main.py   # http://localhost:5000
```

The SQLite database (`website/database.db`) is created automatically on first run.

## Security notes

This is an academic prototype and is **not production-ready**:

- The PUF is simulated: `getPUFResponse()` in `puf.py` returns the key from `DEVICE_PRIVATE_KEY` instead of deriving it from the PUF response. Only use local Ganache keys.
- Never commit real keystores, certificates, private keys or databases. The `.gitignore` excludes them.
