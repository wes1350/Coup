import eventlet
# Eventlet isn't compatible with some python modules (e.g. time) so monkeypatch to resolve 
# bugs that result from such conflicts
eventlet.monkey_patch()
from flask import Flask, render_template, request, g
from flask_socketio import SocketIO, send, emit
from Engine import Engine
from GameInfo import GameInfo
import random
from utils.argument_parsing import parse_args
import time

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

@socketio.on('observer_connect')
def mark_as_observer():
    observers[request.sid] = {}
    if get_id_from_sid(request.sid) in clients:
        del clients[get_id_from_sid(request.sid)]

@socketio.on('start_observer')
def start_as_observer(n_agents):
    print(f"Waiting for {n_agents} agents to connect before starting...")
    # Need to check here not for the number of clients, but for the number of AI, so that we give enough time 
    # to mark AIs as AI, so that we send them AI-compatible messages. Setting sleep to something low (e.g. 0.0001) 
    # and not waiting for us to mark them as AI will result in us treating them like humans,
    # And so the agents never respond since we don't send them the correct messages.
    # Will need to change this a bit if we want to allow human players to mix with Scheduler,
    # Since this assumes all players from Scheduler are AIs
    while len([c for c in clients if clients[c]["ai"]]) < n_agents:
        time.sleep(0.001)
        pass
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
        clients_keys = list(clients.keys())
        random_keys = [i for i in range(len(clients))]
        if not keep_client_order:
            random.shuffle(random_keys)
        shuffled_clients = {}
        for i, k in enumerate(random_keys):
            shuffled_clients[k] = clients[clients_keys[i]]
        clients = shuffled_clients

        game_info = GameInfo()
        game_info.ai_players = [c for c in clients if clients[c]["ai"]]
        engine = Engine(emit_to_client, broadcast, retrieve_response, game_info=game_info, n_players=len(clients), **parsed_args)
        broadcast(game_info.config_settings, "settings")
        winner = engine.run_game()
        socketio.stop()

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
    sender_id = get_id_from_sid(request.sid)
    print("Got an action from player {}: ".format(sender_id) + message)
    clear_old_info(sender_id)
    clients[sender_id]["response"] = message

if __name__ == '__main__':
    parsed_args = parse_args()
    keep_client_order = parsed_args["keep_client_order"]
    started = False
    clients = {} 
    observers = {}
    socketio.run(app, host='0.0.0.0')
