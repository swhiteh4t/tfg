from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from website.blockchainops import CipherOps
from website.io import readContractAddress, writeContractAddress
from .models import Device
from . import db
import os

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
        cipherops = CipherOps.getInstance()
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
