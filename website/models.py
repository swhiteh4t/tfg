from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(64))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    hostname = db.Column(db.String(64), unique=True)
    owner = db.Column(db.String(64))
    public = db.Column(db.String(128))
    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    devices = db.relationship("Device")
    contracts = db.relationship("Contract")


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(64))
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
