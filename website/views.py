from urllib import response
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Device
import pypuf
import os,json
from website.cipherops import decrypt,encrypt
from website.puf import getPUFResponse

views = Blueprint("views", __name__)


@views.route("/", methods=['GET', 'POST'])
@login_required
def home():      
    return render_template("home.html", user=current_user)

@views.route("/create-device", methods=['GET', 'POST'])
@login_required
def createDevices():
    if request.method == "POST":
        hostname = request.form.get("hostname")
        contract = request.form.get("contract-selection")
        device = Device.query.filter_by(hostname=hostname).first()
        print(contract)
        if not(device) and contract is not None:
            #Generate the puf
            puf = getPUFResponse()
            #Get address
            address = getBCA()
            print(current_user.username)
            
            jsonString = json.loads(f.read())
            print(jsonString)
            flash("Device registered with address " + address, category='sucess')
        else:
            flash('Hostname already exists', category='error')
    return render_template("create-devices.html", user=current_user, address=address)

@views.route("/new-contract", methods=['GET', 'POST'])
@login_required
def contracts():
    return render_template("new-contract")