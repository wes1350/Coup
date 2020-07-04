"""An Agent that always takes Income unless forced to Coup, and that never Blocks or Challenges."""

import socketio
import json

sio = socketio.Client()

@sio.on('ai')
def on_prompt(message):
    print("ON PROMPT:", message)
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

def react(message : dict):
    print(message)
    if message["type"] == "action":
        return decide_action(message["options"]) 
    elif message["type"] == "reaction":
        return decide_reaction(message["options"]) 
    elif message["type"] == "card_selection":
        return decide_card(message["options"]) 
    elif message["type"] == "exchange":
        raise Exception("Income Agent shouldn't ever exchange")
    else:
        assert False

def decide_action(actions : dict):
    if "Income" in actions:
        return "Income"
    else:
        if "Coup" in actions:
            if actions["Coup"]:
                return "Coup " + str(actions["Coup"][0])
        assert False

def decide_reaction(reactions):
    return "Pass"

def decide_card(cards):
    return cards[0]


sio.connect('http://localhost:5000')
