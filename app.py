from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin

app = Flask(__name__)
# CORS(app, support_credentials=True)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

@app.route('/')
def index():
    return render_template('index.html')


# Handler for a message recieved over 'connect' channel
# @socketio.on('connect')
# def test_connect():
#     assert False
#     emit('after connect',  {'data':'Lets dance'})

if __name__ == '__main__':
    socketio.run(app)#, host='0.0.0.0')
