import json
from . import Agent

class IncomeAgent(Agent):
    def __init__(self):
        super().__init__()
    
    def react(self, message):
        if message["type"] == "action":
            return self.decide_action(message["options"]) 
        elif message["type"] == "reaction":
            return self.decide_reaction(message["options"]) 
        elif message["type"] == "card_selection":
            return self.decide_card(message["options"]) 
        elif message["type"] == "exchange":
            return self.decide_exchange(message["options"]) 
            
    def decide_action(self, actions : dict):
        if "Income" in actions:
            return "Income"
        else:
            if "Coup" in actions:
                if actions["Coup"]:
                    return "Coup " + str(actions["Coup"][0])
            assert False

    def decide_reaction(self, reactions):
        return "Pass"

    def decide_card(self, cards):
        return cards[0]

    def decide_exchange(self, options):
        return " ".join([str(i) for i in range(options["n"])])
        
