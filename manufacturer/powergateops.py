import os
from pathlib import Path
from pygate_grpc.client import PowerGateClient
from website.blockchainops import CipherOps


class PowerGateOps:

    __instance = None
    __hostName = "127.0.0.1:5002"
    __client = None

    @staticmethod
    def getInstance():
        if PowerGateOps.__instance == None:
            PowerGateOps()
        return PowerGateOps.__instance

     # Constructor function
    def __init__(self):
        if PowerGateOps.__instance != None:
            pass
        else:
            PowerGateOps.__instance = self
            PowerGateOps.__client = PowerGateClient(
                PowerGateOps.__hostName, False)

    @staticmethod
    def retrieveFile(cid, token):
        check = PowerGateOps.__client.data.cid_info(cid, token)
        print("Checking CID storage...")
        print(check)

        # Get the data back
        print("Retrieving file " + cid + "...")
        file_bytes = PowerGateOps.__client.data.get(cid, token)
