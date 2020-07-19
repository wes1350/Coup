import eventlet
# Eventlet isn't compatible with some python modules (e.g. time) so monkeypatch to resolve 
# bugs that result from such conflicts
eventlet.monkey_patch()
from flask import Flask, render_template, request, g, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from Engine import Engine
from GameInfo import GameInfo
import random, time, subprocess
import threading, subprocess
from utils.argument_parsing import parse_args

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

def get_id_from_sid(sid):
    room = sids_to_rooms[sid]
    for c in game_rooms[room]["clients"]:
        if game_rooms[room]["clients"][c]["sid"] == sid:
            return c
    raise ValueError("Invalid sid request")

@app.route('/', methods=('GET', 'POST'))
def startpage():
    if request.method == "POST":
        username = request.form["username"]
        room = request.form["room"]

        return redirect(url_for('room', room=room))
    return render_template('startpage.html')

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
    def run_agent():
        try:
            subprocess.run(f"python3 ./agents/{bot_type}.py {room}", shell=True, check=False)
            print('done')
        except BaseException:
            assert False
            pass 
    thread = threading.Thread(target=run_agent)
    thread.start()
    thread.join()

def broadcast_to_room(room):
    def broadcast(msg, tag=None):
        """Send a message to all clients."""
        room = sids_to_rooms[request.sid]
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

if __name__ == '__main__':
    parsed_args = parse_args()
    keep_client_order = parsed_args["keep_client_order"]
    game_rooms = {}
    sids_to_rooms = {}
    socketio.run(app, host='0.0.0.0')
