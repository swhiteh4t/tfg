from flask import Blueprint, render_template, flash, request, redirect, url_for
from .models import User
import bcrypt
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email =  request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if bcrypt.checkpw(password.encode(), user.password):
                flash("Logged in sucessfuly!", category='success')
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect log in details", category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/signup", methods=["GET", "POST"])
def sing_up():
    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        password1 = request.form.get("password")
        password2 = request.form.get("password2")
        user = User.query.filter_by(email=email).first()    
        
        if user:
            flash("User alredy exists!", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 4 characters", category="error")
        elif len(firstName) < 2:
            flash("First Name should be greater that two characters", category="error")
        elif len(password1) < 7:
            flash("The password should be at least 7 characters", category="error")
        elif password1 != password2:
            flash("Passwords should match!")
        else:
            new_user = User(email=email, firstName=firstName, password=bcrypt.hashpw(password1.encode(),bcrypt.gensalt()))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))
            
    return render_template("signup.html", user=current_user)
