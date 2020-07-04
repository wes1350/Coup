import socketio
import json

def start():
    sio = socketio.Client()
    sio.connect('http://localhost:5000')

@sio.on('ai')
def on_prompt(message):
    response = react(json.loads(message))
    sio.emit("action", response)

@sio.event
def connect():
    print("I'm connected!")
    sio.emit("ai_connect")

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")
