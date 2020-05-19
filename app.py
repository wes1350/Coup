from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    buttons = ["Start", "Income", "Foreign Aid", "Tax", "Steal", "Exchange", "Assassinate", "Coup", "Block", "Challenge"]
    return render_template('index.html', buttons=buttons)

# Handler for a message received over 'connect' channel
@socketio.on('connect')
def test_connect():
    emit('after connect',  {'data':'Client connected'})

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))


if __name__ == '__main__':
    socketio.run(app)#, host='0.0.0.0')
