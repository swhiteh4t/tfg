from flask import Blueprint, render_template, flash, request, redirect, url_for
from .models import User
import bcrypt
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    created = True if User.query.get(1) else False
    if request.method == 'POST':
        username =  request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            if bcrypt.checkpw(password.encode(), user.password):
                flash("Logged in sucessfuly!", category='success')
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect log in details", category='error')
        else:
            flash('Username does not exist.', category='error')
    created = True if User.query.get(1) else False
    return render_template("login.html", user=current_user, created=created)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/signup", methods=["GET", "POST"])
def sing_up():
    if User.query.get(1) and not(current_user.is_authenticated):
        return render_template("404.html"), 404
    else:
        if request.method == "POST":
            username = request.form.get("username")
            password1 = request.form.get("password")
            password2 = request.form.get("password2")
            address = request.form.get("address")
            private_key = request.form.get("private-key")
            user = User.query.filter_by(username=username).first()    

            if user:
                flash("User alredy exists!", category="error")
            elif re.match(r'^(?![-._])(?!.*[_.-]{2})[\w.-]{6,30}(?<![-._])$',username) is None:
                flash("Username should be at least 6 alphanumeric characters long", category="error")
            elif re.fullmatch(r'[A-Za-z0-9@#$%^&+<>=]{8,}', password1) is None:
                flash("The password must have uppercase and undercase letters, a number, a special character @#$%^&+=<> and 8 characters long", category="error")
            elif password1 != password2:
                flash("Passwords should match!")
            else:
                new_user = User(username=username, password=bcrypt.hashpw(password1.encode(),bcrypt.gensalt()))
                db.session.add(new_user)
                db.session.commit()
                flash("Account created!", category="success")
                login_user(new_user, remember=True)
                return redirect(url_for('views.home'))
            
        
        return render_template("signup.html", user=current_user)
