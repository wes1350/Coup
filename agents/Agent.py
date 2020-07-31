"""Base class for Agents."""
import json

if __name__ == "Agent":
    from utils.game import *
    from utils.responses import *
    from utils.network import *
else:
    from .utils.game import *
    from .utils.responses import *
    from .utils.network import *

class Agent:
    def __init__(self, verbose=False):
        self.verbose = verbose
        pass

    def __str__(self):
        return type(self).__name__

    def update_wrapper(self, event):
        event_info = json.loads(event) if isinstance(event, str) else event
        if isinstance(event_info, str):
            event_info = json.loads(event_info)
            if "info" in event_info:
                if isinstance(event_info["info"], str):
                    event_info["info"] = json.loads(event_info["info"])
        else:
            if "info" in event_info:
                if isinstance(event_info["info"], str):
                    event_info["info"] = json.loads(event_info["info"])
        if self.verbose:
            print("Updating with event: ", json.dumps(event_info, indent=4))
        self.update(event_info)

    def update(self, event):
        pass

    def react(self, event_type : str, options : dict):
        options = json.loads(options) if isinstance(options, str) else options
        if event_type == "action":
            response = self.decide_action(options) 
        elif event_type == "reaction":
            response = self.decide_reaction(options) 
        elif event_type == "card_selection":
            response = str(self.decide_card(options))
        elif event_type == "exchange":
            response = self.decide_exchange(options) 
        else:
            if not isinstance(event_type, str):
                raise ValueError("event_type must be a string type")
            else:
                raise ValueError("Received unknown event type: " + event_type)
        if response is None:
            raise Exception(("Agent did not return a value for its response. "
                             "Make sure to return a value (e.g. return income()) when choosing a response."))
        if self.verbose:
            print("Reacting to:", json.dumps(options, indent=4))
            print("Sending response", response, type(response))
        return response

    def unimplemented_response(self, event_type : str):
        def raiser(options):
            raise NotImplementedError("Responding to " + event_type + " not implemented")
        return raiser

    def decide_action(self, options):
        return self.unimplemented_response("actions")(options)

    def decide_reaction(self, options):
        return self.unimplemented_response("reactions")(options)

    def decide_card(self, options):
        return self.unimplemented_response("card selection")(options)

    def decide_exchange(self, options):
        return self.unimplemented_response("exchange")(options)