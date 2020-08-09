"""Handlers for Flask routes"""
import datetime
from flask import render_template, request, g, redirect, url_for, make_response, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_login import current_user, login_user, logout_user
from coup import app, db
from coup.models import User
from coup.socketio_handlers import rt

jwt = JWTManager(app)

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

@app.route('/rooms', methods=('GET', 'POST'))
@jwt_required
def rooms():
    try:
        if request.method == "GET":
            return jsonify(list(rt.game_rooms.values())), 200
        elif request.method == "POST":
            data = request.get_json(force=True)
            if create_room(data['roomName']) is None:
                return jsonify('room already exist'), 400
            return jsonify('room created'), 201
    except Exception as e:
        print(e)
        return jsonify({'status': 'Server error'}), 500

@app.route('/users/register', methods=('POST',))
def registerReact():
    if request.method == "POST":
        try:
            data = request.get_json(force=True)
            username = data["username"]
            password = data["password"]

            if User.query.filter_by(username=username).first() is not None:
                raise Exception("username not available.")
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Successfully registered',
            }
            return make_response(jsonify(response_object)), 201
        except Exception as e:
            print(e)
            response_object = {
                'status': 'fail',
                'message': str(e)
                }
            return make_response(jsonify(response_object)), 401

@app.route('/users/authenticate', methods=('POST', ))
def authenticate():
    try:
        data = request.get_json(force=True)
        username = data["username"]
        password = data["password"]
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return jsonify({'status': 'User not found'}), 404 
        expires = datetime.timedelta(hours=1)
        return jsonify({'username': username, 'access_token': create_access_token(identity=user.id, expires_delta=expires)}), 200
    except Exception as e:
        print(e)
        return  jsonify({'status': 'server error'}), 500

def create_room(name):
    if name not in rt.game_rooms:
        rt.game_rooms[name] = {"name": name, "clients": {}, "observers": {}, "started": False}
        print(rt.game_rooms)
        return name