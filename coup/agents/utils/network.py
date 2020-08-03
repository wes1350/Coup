"""Utilities for interacting with the Game Engine over the network."""

import socketio
import json, time


def start(agent, room):

    sio = socketio.Client()

    @sio.on('ai_query')
    def on_prompt(message):
        print("Reacting to:", message)
        loaded_msg = json.loads(message)
        options = json.loads(loaded_msg["options"]) if isinstance(loaded_msg["options"], str) \
                                                    else loaded_msg["options"]
        response = agent.react(loaded_msg["type"], options)
        print("Sending response", response, type(response))
        sio.emit("action", response)

    @sio.on('ai_info')
    def update_wrapper(event):
        event_info = json.loads(event)
        print("Updating with event: ", event_info)
        if isinstance(event_info, str):
            event_info = json.loads(event_info)
            if "info" in event_info:
                if isinstance(event_info["info"], str):
                    event_info["info"] = json.loads(event_info["info"])
        else:
            if "info" in event_info:
                if isinstance(event_info["info"], str):
                    event_info["info"] = json.loads(event_info["info"])
        print(event_info)
        agent.update(event_info)

    @sio.on('game_over')
    def cleanup(game_over_msg=None):
        time.sleep(1)
        sio.disconnect()

    @sio.event
    def connect():
        print("Connected as bot player")
        sio.emit("join_room", room)
        sio.emit("ai_connect")

    @sio.event
    def connect_error():
        print("The connection failed!")

    @sio.event
    def disconnect():
        print("Disconnected as bot player")
        sio.disconnect()

    sio.connect('http://localhost:5000')
