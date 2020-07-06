import eventlet
# Eventlet isn't compatible with some python modules (e.g. time) so monkeypatch to resolve 
# bugs that result from such conflicts
eventlet.monkey_patch()
from flask import Flask, render_template, request, g, jsonify, abort
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS

from Engine import Engine
from GameInfo import GameInfo

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")
rooms = {}

@app.route('/')
def index():
    g.started = False
    return render_template('index.html')

@app.route('/api/name', methods=['POST', 'GET'])
# @cross_origin()
def name():
    print(clients)
    print(request.json)
    if request.method == 'POST':
        if 'name' not in request.json and 'sid' not in request.json:
            abort(400)
        else:
            clients[request.json['sid']]['name'] = request.json['name']
            return jsonify({'name': request.json['name']}), 201
    elif request.method == 'GET':
        if 'sid' not in request.json:
            abort(400)
        else:
            return clients[request.json['sid']]['name'], 200

@app.route('/api/rooms', methods=['POST'])
def create_room():
    if len(rooms.keys() == 0):
        rooms[1] = [request.json['sid']]
        return jsonify({}), 201
    else:
        existing_rooms = rooms.keys()
        new_room_id = max(existing_rooms) + 1
        rooms[new_room_id] = [request.json['sid']]
        return jsonify({}), 201

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    return rooms.keys

@socketio.on('connect')
def on_connect():
    print(clients)
    print(started)

    clients[request.sid] = {"response": "No response"}
    print("Client connected")
    print(clients)

@socketio.on('disconnect')
def on_disconnect():
    del clients[request.sid]
    print("Client disconnected")
    print(clients)

@socketio.on('start game')
def on_start():
    global started
#     global clients
    print(clients)
    # TODO: need to change this to allow multiple games
    if not started:  # Don't allow multiple starts
        print("Starting")
        broadcast("",  "start game")
        started = True
        g.started = True
        game_info = GameInfo()
        g.game_info = game_info
        # get the room of clients
        players_dict = {key: value['name'] for key, value in clients.items()} 
        print('players_dict', players_dict)
        engine = Engine(players_dict, emit_to_client, broadcast, retrieve_response, game_info=game_info, n_players=len(clients))
        broadcast(game_info.config_settings, "settings")
        winner = engine.run_game()

def broadcast(msg, tag=None):
    """Send a message to all clients."""
    clear_old_info()
    if tag is None:
        send(msg, broadcast=True)
    else:
        for client in clients:
            emit_to_client(msg, client, tag)

def emit_to_client(msg, client_id, tag=None):
    # Clear response before whispering, to ensure we don't keep a stale one
    clients[client_id]["response"] = "No response"
    if tag is None:
        socketio.send(msg, room=client_id)
    else:
        emit(tag, msg, room=client_id)

def retrieve_response(client_id):
    """Get the current stored response corresponding to the requested client."""
    return clients[client_id]["response"]

def clear_old_info(specific_client=None):
    # Erase outdated info
    for client in ([specific_client] if specific_client else clients):
        emit_to_client("", client, "error")
        emit_to_client("", client, "prompt")

@socketio.on('action')
def store_action(message):
    print("Got an action: " + message)
    clear_old_info(request.sid)
    clients[request.sid]["response"] = message

if __name__ == '__main__':
    started = False
    clients = {}
    socketio.run(app, host='0.0.0.0')
