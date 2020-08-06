import eventlet
# Eventlet isn't compatible with some python modules (e.g. time) so monkeypatch to resolve 
# bugs that result from such conflicts
eventlet.monkey_patch()
from flask import Flask, render_template, request, g, redirect, url_for, flash, make_response, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from AppConfig import AppConfig
from Engine import Engine
from GameInfo import GameInfo
import random, time, subprocess
from utils.argument_parsing import parse_args

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# app.secret_key = b'\xc92`\x0b\x01\xb1\xfb\x7f\x8e\x94\xef\t\x95\\\xf7\xa6'
app.config.from_object(AppConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="https://localhost:3000")
login_manager = LoginManager(app)
import models  # for importing db models for db migration


def get_id_from_sid(sid):
    room = sids_to_rooms[sid]
    for c in game_rooms[room]["clients"]:
        if game_rooms[room]["clients"][c]["sid"] == sid:
            return c
    raise ValueError("Invalid sid request")

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

@app.route('/', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = "rememberme" in request.form and request.form["rememberme"] == "on"

        user = models.User.query.filter_by(username=username).first()
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

        user = models.User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register')

@app.route('/registerReact', methods=('POST',))
def registerReact():
    if current_user.is_authenticated:
        response_object = {
            'status': 'fail',
            'message': 'User already signed in.',
        }
        return make_response(jsonify(response_object)), 202 

    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]

            user = models.User(username=username)
            user.set_password(password)
            auth_token = user.encode_auth_token()
            print(auth_token)
            db.session.add(user)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Successfully registered',
                'auth_token': auth_token.decode()
            }
            return make_response(jsonify(response_object)), 201
        except Exception as e:
            print(e)
            response_object = {
                'status': 'fail',
                'message': 'Some error occured. Please try again'
            }
            return make_response(jsonify(response_object)), 401

@app.route('/users/authenticate', methods=('POST', ))
def authenticate():
    try:
        data = request.get_json(force=True)
        username = data["username"]
        password = data["password"]
        user = models.User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return jsonify({'status': 'User not found'}), 404 
        login_user(user, remember=True)
        return jsonify({'username': username, 'authToken': user.encode_auth_token()}), 200
    except Exception as e:
        print(e)
        return  jsonify({'status': 'server error'}), 500

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

@app.route('/rooms', methods=('GET', 'POST'))
def rooms():
    if current_user.is_authenticated:
        try:
            if request.method == "GET":
                # will need to verfiy that the authToken is good
                return jsonify(game_rooms), 200
            elif request.method == "POST":
                data = request.get_json(force=True)
                if create_room(data['roomName']) is None:
                    return jsonify('room already exist'), 400
                return jsonify('room created'), 201
        except Exception as e:
            print(e)
            return jsonify({'status': 'Server error'}), 500
    else:
        return jsonify({'status': 'unauthorized'}), 401

@app.route('/room/<room>')
def room(room):
    return render_template('room.html', room=room)

@socketio.on('join_room')
def on_join(room):
    if room not in game_rooms:
        game_rooms[room] = {"clients": {}, "observers": {}, "started": False}
    join_room(room)
    new_index = max(game_rooms[room]["clients"].keys()) + 1 if len(game_rooms[room]["clients"]) > 0 else 0  
    game_rooms[room]["clients"][new_index] = {"sid": request.sid, "response": "No response", "ai": False}
    sids_to_rooms[request.sid] = room
    send("A new player has joined room {}!".format(room), room=room)

@socketio.on('leave_room')
def on_leave(room):
    leave_room(room)
    send("A player has left room {}!".format(room), room=room)

@socketio.on('connect')
def on_connect():
#     new_index = max(clients.keys()) + 1 if len(clients) > 0 else 0  
#     clients[new_index] = {"sid": request.sid, "response": "No response", "ai": False}
    print("Client connected")
#     print(clients)

@socketio.on('ai_connect')
def mark_as_ai():
    room = sids_to_rooms[request.sid]
    for c in game_rooms[room]["clients"]:
        if game_rooms[room]["clients"][c]["sid"] == request.sid:
            game_rooms[room]["clients"][c]["ai"] = True
            print("Marked {} as AI".format(c))
            break
    else:
        raise Exception("Didn't mark as AI, probably executed AI connect before joining room was completed")

@socketio.on('observer_connect')
def mark_as_observer():
    room = sids_to_rooms[request.sid]
    game_rooms[room]["observers"][request.sid] = {}
    if get_id_from_sid(request.sid) in game_rooms[room]["clients"]:
        del game_rooms[room]["clients"][get_id_from_sid(request.sid)]

@socketio.on('start_observer')
def start_as_observer(n_agents):
    print(f"Waiting for {n_agents} agents to connect before starting...")
    # Need to check here not for the number of clients, but for the number of AI, so that we give enough time 
    # to mark AIs as AI, so that we send them AI-compatible messages. Setting sleep to something low (e.g. 0.0001) 
    # and not waiting for us to mark them as AI will result in us treating them like humans,
    # And so the agents never respond since we don't send them the correct messages.
    # Will need to change this a bit if we want to allow human players to mix with Scheduler,
    # Since this assumes all players from Scheduler are AIs
    room = sids_to_rooms[request.sid]
    while len([c for c in game_rooms[room]["clients"] if game_rooms[room]["clients"][c]["ai"]]) < n_agents:
        time.sleep(0.001)
        pass
    on_start(room)

@socketio.on('disconnect')
def on_disconnect():
#     try:
#         del game_rooms[room]["clients"][get_id_from_sid(request.sid)]
    print("Client disconnected")
#     except ValueError:
#         del game_rooms[room]["observers"][request.sid]
#         print("Observers disconnected")

@socketio.on('start game')
def on_start(passed_room=None):
    if passed_room is not None:
        room = passed_room
    else:
        print(sids_to_rooms)
        room = sids_to_rooms[request.sid]
    if not game_rooms[room]["started"]:  # Don't allow multiple starts
        print("Starting")
        broadcast_to_room(room)("",  "start game")
        game_rooms[room]["started"] = True
        # shuffle clients randomly 
        clients_keys = list(game_rooms[room]["clients"].keys())
        random_keys = [i for i in range(len(game_rooms[room]["clients"]))]
        if not keep_client_order:
            random.shuffle(random_keys)
        shuffled_clients = {}
        for i, k in enumerate(random_keys):
            shuffled_clients[k] = game_rooms[room]["clients"][clients_keys[i]]
        game_rooms[room]["clients"] = shuffled_clients

        game_info = GameInfo()
        game_info.ai_players = [c for c in game_rooms[room]["clients"] if game_rooms[room]["clients"][c]["ai"]]
        engine = Engine(emit_to_client_in_room(room), broadcast_to_room(room), retrieve_response_in_room(room),
                        game_info=game_info, n_players=len(game_rooms[room]["clients"]), **parsed_args)
        broadcast_to_room(room)(game_info.config_settings, "settings")
        winner = engine.run_game()
        socketio.stop()

@socketio.on('action')
def store_action(message):
    room = sids_to_rooms[request.sid]
    sender_id = get_id_from_sid(request.sid)
    print("Got an action from player {}: ".format(sender_id) + message)
    clear_old_info(room, sender_id)
    game_rooms[room]["clients"][sender_id]["response"] = message

@socketio.on('add_bot')
def add_bot(bot_type):
    room = sids_to_rooms[request.sid]
    broadcast_to_room(room)(f"Adding {bot_type} to game", "info")
    def run_agent():
        try:
            subprocess.run(f"python3 ./agents/{bot_type}.py {room}", shell=True, check=False)
            print('done')
        except BaseException:
            assert False
            pass 
#     thread = threading.Thread(target=run_agent)
    thread = socketio.start_background_task(target=run_agent)
#     thread.start()
    thread.join()

def broadcast_to_room(room):
    def broadcast(msg, tag=None):
        """Send a message to all clients."""
        clear_old_info(room)
        if tag is None:
            socketio.send(msg, room=room)
        else:
            for client in game_rooms[room]["clients"]:
                emit_to_client_in_room(room)(msg, client, tag, clear=False)
    return broadcast

def emit_to_client_in_room(room):
    def emit_to_client(msg, client_id, tag=None, clear=True):
        # Clear response before whispering, to ensure we don't keep a stale one
        if clear:
            game_rooms[room]["clients"][client_id]["response"] = "No response"
        if tag is None:
            socketio.send(msg, room=game_rooms[room]["clients"][client_id]["sid"])
        else:
            emit(tag, msg, room=game_rooms[room]["clients"][client_id]["sid"])
    return emit_to_client

def retrieve_response_in_room(room):
    def retrieve_response(client_id):
        """Get the current stored response corresponding to the requested client."""
        return game_rooms[room]["clients"][client_id]["response"]
    return retrieve_response

def clear_old_info(room, specific_client=None):
    # Erase outdated info
    for client in ([specific_client] if specific_client is not None else game_rooms[room]["clients"]):
        emit_to_client_in_room(room)("", client, "error")
        emit_to_client_in_room(room)("", client, "prompt")

def create_room(name):
    if name not in game_rooms:
        game_rooms[name] = {"name": name, "clients": {}, "observers": {}, "started": False}
        print(game_rooms)
        return name

if __name__ == '__main__':
    parsed_args = parse_args()
    keep_client_order = parsed_args["keep_client_order"]
    game_rooms = {}
    sids_to_rooms = {}
    login_manager.init_app(app)
    socketio.run(app, host='0.0.0.0')
