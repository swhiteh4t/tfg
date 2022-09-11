import re
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from website.blockchainops import BlockChainOps
from website.cipherops import encrypt
from website.io import readContractAddress, writeContractAddress
from website.powergateops import PowerGateOps
from .models import Certificate, Device
from . import db
import os
from website.certificateops import cert_gen

views = Blueprint("views", __name__)


@views.route("/", methods=['GET', 'POST'])
@login_required
def home():
    contractAddress = readContractAddress()
    if request.method == "POST":
        writeContractAddress(request.form.get("contract"))
        return render_template("home.html", user=current_user, contract=request.form.get("contract"))

    return render_template("home.html", user=current_user, contract=contractAddress)


@views.route("/engagement", methods=["GET", "POST"])
@login_required
def engageDevices():
    devices = Device.query.all()
    if request.method == "POST":
        device = request.form.get("device-selection")
        fileName = request.form.get("filename")
        password = request.form.get("password")
        dev = Device.query.filter_by(address=device).first()
        cipherops = BlockChainOps.getInstance()
        engageData = cipherops.engageDevice(
            fileName, password, dev.public, device)
        if len(engageData) > 0:
            flash("Engaged sucessfuly", category="sucess")

    return render_template("engagement.html", user=current_user, devices=devices)


@views.route("/register-device", methods=["GET", "POST"])
@login_required
def createDevices():
    if request.method == "POST":
        hostname = request.form.get("hostname")
        address = request.form.get("device-address")
        public = request.form.get("public")
        device = Device.query.filter_by(hostname=hostname).first()
        if not (device):
            new_device = Device(
                address=address,
                public=public,
                hostname=hostname,
                user_id=current_user.id,
            )
            db.session.add(new_device)
            db.session.commit()
            flash(
                "Device registered with address "
                + address
                + " waiting for owner engagement"
                + " Public key -> "
                + public,
                category="sucess",
            )
        else:
            flash("Device already registered", category="error")
    return render_template("register-devices.html", user=current_user)


@views.route("/list-devices")
@login_required
def listDevices():
    contract = readContractAddress()
    return render_template(
        "list-devices.html", user=current_user, contract=contract
    )


@views.route("/create-certificate", methods=['GET', 'POST'])
@login_required
def createCertificate():
    devices = Device.query.all()
    if request.method == "POST":
        device = request.form.get("device-selection")
        state_province = request.form.get("state-province")
        locality = request.form.get("locality")
        organization = request.form.get("organization")
        common_name = request.form.get("common-name")
        email = request.form.get("email")
        validity = request.form.get("validity")
        countryname = request.form.get("country-name")
        pk = device + ".key"
        cert = device + ".crt"
        password = request.form.get("password")
        hash, hashH = cert_gen(commonName=common_name, countryName=countryname,
                               localityName=locality, stateOrProvinceName=state_province, organizationName=organization,
                               emailAddress=email, validityEndInSeconds=int(validity), KEY_FILE=pk, CERT_FILE=cert)
        queriedDevice = Device.query.filter_by(address=device)
        powergate = PowerGateOps.getInstance()
        user = powergate.getUser()
        cid = powergate.storeFile(os.path.join(
            os.getcwd(), "website", "certificates", cert), user.token)
        bk = BlockChainOps.getInstance()
        bk.setCertificateHash("owner", password, hash, device)
        device = Device.query.filter_by(address=device).first()
        secret = bk.getSecret("owner", password, device.public)
        print("Secret " + secret.hex())
        ct = encrypt(secret, cid + ","+user.token)
        print(ct)
        bk.setCertificateToken("owner", password, ct, device.address)
        #os.getcwd(), "website", "certificates", CERT_FILE
        new_device = Certificate(
            cid=cid,
            hash=hashH,
            token=ct,
            device_id=device.id,
        )
        db.session.add(new_device)
        db.session.commit()
        flash("New certificate for device " +
              device.address + " created " + user.token + " CID " + cid, category="sucess")
    return render_template("create-certificate.html", user=current_user, devices=devices)


@views.route("/list-certificates")
@login_required
def listCertificates():
    certificates = Certificate.query.all()
    return render_template(
        "list-certificates.html", user=current_user, certificates=certificates
    )
