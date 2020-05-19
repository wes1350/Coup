from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from Engine import Engine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    buttons = ["Start", "Income", "Foreign Aid", "Tax", "Steal", "Exchange", "Assassinate", "Coup", "Block", "Challenge", "0", "1"]
    state = "Everyone wins!"
    return render_template('index.html', buttons=buttons, state=state)

@socketio.on('connect')
def on_connect():
    print(clients)
    print(started)
    clients[len(clients)] = request.sid
    print("Client connected")
    print(clients)

@socketio.on('disconnect')
def on_disconnect():
    for client_id in clients:
        if clients[client_id] == request.sid:
            clients.remove(entry)
    print("Client disconnected")
    print(clients)

@socketio.on('start game')
def on_start():
    global started
#     global clients
    print(clients)
    if not started:  # Don't allow multiple starts
        print("Starting")
        started = True
        engine = Engine(send_to_client, lambda msg: send(msg, broadcast=True), emit_to_client, n_players=len(clients))
        winner = engine.run_game()

def send_to_client(msg, client_id):
    socketio.send(msg, room=clients[client_id])

def emit_to_client(name, msg, client_id):
    emit(name, msg, room=clients[client_id])

if __name__ == '__main__':
    started = False
    clients = {}
    socketio.run(app)#, host='0.0.0.0')
