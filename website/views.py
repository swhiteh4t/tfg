from urllib import response
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from . import db
from .models import Device, Contract
import pypuf
import os, json
from website.blockchainops import CipherOps

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route("/create-device", methods=["GET", "POST"])
@login_required
def createDevices():
    if request.method == "POST":
        hostname = request.form.get("hostname")
        owner = request.form.get("owner-address")
        contract = request.form.get("contract-selection")
        filename = request.form.get("filename")
        password = request.form.get("password")
        device = Device.query.filter_by(hostname=hostname).first()
        print(owner)
        if not (device) and contract is not None:
            # Get address
            cipherops = CipherOps.getInstance()
            address, publicKey = cipherops.createDeviceToken(
                owner, contract, filename, password
            )
            if publicKey is not None:
                flash(
                    "Device registered with address "
                    + address
                    + " waiting for owner engagement"
                    + " Public key -> "
                    + publicKey,
                    category="sucess",
                )
                new_device = Device(
                    address=address,
                    public=publicKey,
                    hostname=hostname,
                    owner=current_user.username,
                    user_id=current_user.id,
                )
                db.session.add(new_device)
                db.session.commit()
                render_template(
                    "create-devices.html",
                    user=current_user,
                    address=address,
                    publicKey=publicKey,
                )
            else:
                flash("Device already registered", category="error")
        else:
            flash("Hostname already exists", category="error")
    return render_template("create-devices.html", user=current_user)


@views.route("/list-devices")
@login_required
def listDevices():
    contract = Contract.query.filter_by(user_id=current_user.id).first()
    return render_template(
        "list-devices.html", user=current_user, contract=contract.address
    )


@views.route("/deploy-contract", methods=["GET", "POST"])
@login_required
def deployContract():
    if request.method == "POST":
        contract = Contract.query.filter_by(user_id=current_user.id).first()
        if contract is None:
            fileName = request.form.get("filename")
            password = request.form.get("password")
            cipherops = CipherOps.getInstance()
            address = cipherops.deployBlockchain(fileName, password)
            new_contract = Contract(address=address, user_id=current_user.id)
            db.session.add(new_contract)
            db.session.commit()
            flash("New contract created with address " + address, category="success")
            return render_template("deploy-contract.html", user=current_user)
        else:
            flash("Contract already deployed " + contract.address, category="error")
            return render_template("deploy-contract.html", user=current_user)
    else:
        return render_template("deploy-contract.html", user=current_user)


@views.route("/list-contracts", methods=["GET", "POST"])
@login_required
def listContract():
    return render_template("list-contract.html", user=current_user)
