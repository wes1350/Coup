from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from Engine import Engine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

clients = []
started = False
n_clients = 0

@app.route('/')
def index():
    buttons = ["Start", "Income", "Foreign Aid", "Tax", "Steal", "Exchange", "Assassinate", "Coup", "Block", "Challenge", "0", "1"]
    state = "Everyone wins!"
    return render_template('index.html', buttons=buttons, state=state)

@socketio.on('connect')
def on_connect():
    clients.append(request.sid)
    print("Client connected")
    emit('after connect',  {'data':'Client connected'})

@socketio.on('disconnect')
def on_disconnect():
    clients.remove(request.sid)
    emit('after disconnect',  {'data':'Client disconnected'})

@socketio.on('start game')
def on_start():
    print("Starting")
    started = True
    n_clients = len(clients)
    engine = Engine()
    if not engine.get_config_status():
        print("\nInvalid configuration: " + engine.get_config_err_msg().split("'")[1])
        print("\nCannot run game; exiting.")
    else:
        winner = engine.run_game()

def send_to_client(msg, client_id):
    send(msg, room=client_id)

def emit_to_client(name, msg, client_id):
    emit(name, msg, room=client_id)

if __name__ == '__main__':
    socketio.run(app)#, host='0.0.0.0')
