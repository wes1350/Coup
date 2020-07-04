"""An Agent that always takes Income unless forced to Coup, and that never Blocks or Challenges."""

if __name__ == "__main__":
    from Agent import Agent
else:
    from .Agent import Agent

class IncomeAgent(Agent):
    def __init__(self):
        super().__init__()
    
    def react(self, message : dict):
        if message["type"] == "action":
            return self.decide_action(message["options"]) 
        elif message["type"] == "reaction":
            return self.decide_reaction(message["options"]) 
        elif message["type"] == "card_selection":
            return self.decide_card(message["options"]) 
        elif message["type"] == "exchange":
            raise Exception("Income Agent shouldn't ever exchange")

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


if __name__ == "__main__":
    ia = IncomeAgent()
