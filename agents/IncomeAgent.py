from . import Agent

class IncomeAgent(Agent):
    def __init__(self):
        super().__init__()
    
    def decide_action(self, actions : dict):
        if "Income" in actions:
            return "Income"
        else:
            raise Exception("Unable to do Income - raising Exception")

    def decide_card(self, cards):
        return cards[0]

    def decide_exchange(self, options):
        return options[0]

    def decide_reaction(self, reactions):
        return reactions[0]
