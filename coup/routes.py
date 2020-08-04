"""Handlers for Flask routes"""

from flask import render_template, request, g, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from coup import app, db
from coup.models import User

@app.route('/', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = "rememberme" in request.form and request.form["rememberme"] == "on"

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=remember)
        return redirect(url_for('home'))

    return render_template('login.html', title='Sign In')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home', methods=('GET', 'POST'))
def home():
    if request.method == "POST":
        room = request.form["room"]
        return redirect(url_for('room', room=room))
    return render_template('home.html')

@app.route('/room/<room>')
def room(room):
    return render_template('room.html', room=room)

