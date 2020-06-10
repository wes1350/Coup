import eventlet
# Eventlet isn't compatible with some python modules (e.g. time) so monkeypatch to resolve 
# bugs that result from such conflicts
eventlet.monkey_patch()
from flask import Flask, render_template, request, g
from flask_socketio import SocketIO, send, emit
from Engine import Engine
from GameInfo import GameInfo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

def get_id_from_sid(sid):
    for c in clients:
        if clients[c]["sid"] == sid:
            return c
    raise ValueError("Invalid sid request")

@app.route('/')
def index():
    g.started = False
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print(clients)
    print(started)

    clients[len(clients)] = {"sid": request.sid, "response": "No response"}
    print("Client connected")
    print(clients)

@socketio.on('disconnect')
def on_disconnect():
    del clients[get_id_from_sid(request.sid)]
    print("Client disconnected")
    print(clients)

@socketio.on('start game')
def on_start():
    global started
#     global clients
    print(clients)
    if not started:  # Don't allow multiple starts
        print("Starting")
        broadcast("",  "start game")
        started = True
        g.started = True
        game_info = GameInfo()
        g.game_info = game_info
        engine = Engine(emit_to_client, broadcast, retrieve_response, game_info=game_info, n_players=len(clients))
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
        socketio.send(msg, room=clients[client_id]["sid"])
    else:
        emit(tag, msg, room=clients[client_id]["sid"])

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
    sender_id = get_id_from_sid(request.sid)
    clear_old_info(sender_id)
    clients[sender_id]["response"] = message

if __name__ == '__main__':
    started = False
    clients = {} 
    socketio.run(app, host='0.0.0.0')
