import eventlet
# Eventlet isn't compatible with some python modules (e.g. time) so monkeypatch to resolve 
# bugs that result from such conflicts
eventlet.monkey_patch()
from flask import Flask, render_template, request, g
from flask_socketio import SocketIO, send, emit
from Engine import Engine
from GameInfo import GameInfo
import random

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
    print(started)
    new_index = max(clients.keys()) + 1 if len(clients) > 0 else 0  
    clients[new_index] = {"sid": request.sid, "response": "No response", "ai": False}
    print("Client connected")
    print(clients)

@socketio.on('ai_connect')
def mark_as_ai():
    for c in clients:
        if clients[c]["sid"] == request.sid:
            clients[c]["ai"] = True
            print("Marked {} as AI".format(c))
            break

@socketio.on('start_observer')
def start_as_observer():
    # joins the game as an observer and starts the game
	for c in clients:
		if clients[c]["sid"] == request.sid:
			print("Removing observer from clients")
			del clients[c]
			observers[request.sid] = {}
			break
	on_start()

@socketio.on('disconnect')
def on_disconnect():
    try:
        del clients[get_id_from_sid(request.sid)]
        print("Client disconnected")
    except ValueError:
        del observers[request.sid]
        print("Observers disconnected")

@socketio.on('start game')
def on_start():
    global started
    global clients
    print(clients)
    if not started:  # Don't allow multiple starts
        print("Starting")
        broadcast("",  "start game")
        started = True
        # shuffle clients randomly
        print(clients)
        clients_keys = list(clients.keys())
        random_keys = [i for i in range(len(clients))]
        random.shuffle(random_keys)
        shuffled_clients = {}
        for i, k in enumerate(random_keys):
            shuffled_clients[k] = clients[clients_keys[i]]
        clients = shuffled_clients
        print(clients)

        game_info = GameInfo()
        game_info.ai_players = [c for c in clients if clients[c]["ai"]]
        engine = Engine(emit_to_client, broadcast, retrieve_response, game_info=game_info, n_players=len(clients))
        broadcast(game_info.config_settings, "settings")
        winner = engine.run_game()
        socketio.stop()
        return
        print('ending server...')

def broadcast(msg, tag=None):
    """Send a message to all clients."""
    clear_old_info()
    if tag is None:
        send(msg, broadcast=True)
    else:
        for client in clients:
            emit_to_client(msg, client, tag, clear=False)

def emit_to_client(msg, client_id, tag=None, clear=True):
    # Clear response before whispering, to ensure we don't keep a stale one
    if clear:
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
    for client in ([specific_client] if specific_client is not None else clients):
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
    observers = {}
    socketio.run(app, host='0.0.0.0')
