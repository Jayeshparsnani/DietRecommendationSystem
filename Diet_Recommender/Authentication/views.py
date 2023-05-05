from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from .. import login_manager, db
from ..Recommender.views import Recommender
Authentication = Blueprint('Authentication', __name__,
                           template_folder='templates/Authentication')


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


@Authentication.route('/login')
def login():
    return render_template('login.html')


@Authentication.route('/login_user', methods=["POST"])
def login_Users():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        print("here")
        flash('Please check your login details and try again.')
        # if the user doesn't exist or password is wrong, reload the page
        return redirect(url_for("Authentication.login"))

    # if the above check passes, then we know the user has the right credentials
    login_user(user)
    return redirect(url_for("Recommender.Dashboard"))


@Authentication.route('/signup')
def signup():
    return render_template('signup.html')


@Authentication.route('/signup', methods=["POST"])
def signup_Users():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    Confirm_pass = request.form.get('pass')
    # if this returns a user, then the email already exists in database
    user = User.query.filter_by(email=email).first()
    if password != Confirm_pass:
        flash('Password and Confirm Password Doesn\'t match')
        return redirect(url_for("Authentication.signup"))

    if user:
        flash('Account already Exists.')
        return redirect(url_for("Authentication.signup"))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name,
                    password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("Authentication.login"))


@Authentication.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("Authentication.login"))
