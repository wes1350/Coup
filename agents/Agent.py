"""Base class for AI agents."""

import socketio
import json

sio = socketio.Client()

class Agent:
    def __init__(self):
        sio.connect('http://localhost:5000')

    @sio.on('ai')
    def on_prompt(self, message):
        resopnse = self.react(json.loads(message))
        sio.emit("action", response)

    def react(self, message : str):
        raise NotImplementedError()

    def update(self, update) -> None:
        """Given an update event, update the internal state to account for it."""
        pass
    
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
