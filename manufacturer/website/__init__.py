import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from website.blockchainops import BlockChainOps


db = SQLAlchemy()
DB_NAME = "database.db"


def getState(addressDev, address):
    bk = BlockChainOps.getInstance()
    return bk.getDeviceState(addressDev, address)


def page_not_found(e):
    return render_template("404.html"), 404


# init our application
def create_app():
    app = Flask(__name__)
    # This key is used to cipher cookies and sensitive data do not hardcode
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.register_error_handler(404, page_not_found)
    db.init_app(app)
    app.jinja_env.globals.update(getState=getState)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import Device, User, Contract

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")
