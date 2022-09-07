from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(150))
    devices = db.relationship("Device")


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.Integer, unique=True)
    address = db.Column(db.String(64), unique=True)
    public = db.Column(db.String(128), unique=True)
    certificate = db.relationship("Certificate")
    talks_to = db.relationship("TalksTo")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.String(256), unique=True)
    hash = db.Column(db.String(64), unique=True)
    token = db.Column(db.String(128))
    device_id = db.Column(db.Integer, db.ForeignKey("device.id"))


class TalksTo(db.Model):
    device = db.Column(db.String(64), primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("device.id"))
