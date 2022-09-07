import os
from pathlib import Path
from pygate_grpc.client import PowerGateClient

from website.io import readPowerGateConfig


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

            PowerGateOps.__config = readPowerGateConfig()
            PowerGateOps.__instance = self
            PowerGateOps.__client = PowerGateClient(
                PowerGateOps.__hostName, False)

    @staticmethod
    def getUser():
        return PowerGateOps.__client.admin.users.create()

    @staticmethod
    def storeFile(path, token):
        staged_file = PowerGateOps.__client.data.stage_file(path, token)
        print("IPFS CID: " + staged_file.cid)

        # Apply the default storage config to the given file
        print("Applying Filecoin storage config to CID...")
        job = PowerGateOps.__client.config.apply(
            staged_file.cid, override=False, token=token)
        return staged_file.cid
