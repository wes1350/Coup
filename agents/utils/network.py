"""Utilities for interacting with the Game Engine over the network."""

import socketio
import json

def unimplemented_response(event_type : str):
    def raiser(options):
        raise NotImplementedError("Responding to " + event_type + " not implemented")
    return raiser

def unimplemented_update():
    def do_nothing(event):
        pass
    return do_nothing

def start(on_action=unimplemented_response("actions"), 
          on_reaction=unimplemented_response("reactions"), 
          on_card=unimplemented_response("card selection"), 
          on_exchange=unimplemented_response("exchanges"),
          update_f=unimplemented_update()):

    sio = socketio.Client()

    @sio.on('ai_query')
    def on_prompt(message):
        print("Reacting to:", message)
        loaded_msg = json.loads(message)
        options = json.loads(loaded_msg["options"]) if isinstance(loaded_msg["options"], str) \
                                                    else loaded_msg["options"]
        response = react(loaded_msg["type"], options)
        print("sending response", response, type(response))
        sio.emit("action", response)

    def react(event_type : str, options : dict):
        if event_type == "action":
            response = on_action(options) 
        elif event_type == "reaction":
            response = on_reaction(options) 
        elif event_type == "card_selection":
            response = str(on_card(options))
        elif event_type == "exchange":
            response = on_exchange(options) 
        else:
            if not isinstance(event_type, str):
                raise ValueError("event_type must be a string type")
            else:
                raise ValueError("Received unknown event type: " + event_type)
        if response is None:
            raise Exception(("Agent did not return a value for its response. "
                             "Make sure to return a value (e.g. return income()) when choosing a response."))
        return response

    @sio.on('ai_info')
    def update(event):
        event_info = json.loads(event)
        print("Updating with event: ", event_info)
        if isinstance(event_info, str):
            event_info = json.loads(event_info)
        update_f(event_info)

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
        sio.disconnect()

    sio.connect('http://localhost:5000')
