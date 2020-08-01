"""An Agent that mimics the most recent possible action done by a player."""

import sys, random

if "." not in __name__:
    from utils.game import *
    from utils.responses import *
    from utils.network import *
    from Agent import Agent
else:
    from .utils.game import *
    from .utils.responses import *
    from .utils.network import *
    from .Agent import Agent

characters_to_moves = {"Ambassador": {"action": ["Exchange"], "block": ["Steal"]},
                       "Assassin": {"action": ["Assassinate"], "block": []},
                       "Captain": {"action": ["Steal"], "block": ["Steal"]}, 
                       "Contessa": {"action": [], "block": ["Foreign Aid", "ForeignAid"]},
                       "Duke": {"action": ["Tax"], "block": ["Tax"]}}

class HonestAgent(Agent):
    def __init__(self):
        super().__init__()
        self.alive_cards = {"Ambassador": False, "Assassin": False, "Captain": False, 
                            "Contessa": False, "Duke": False}

    def update(self, event):
        if event["event"] == "state":
            me = event["info"]["playerId"]
            # Reset our hand
            for character in self.alive_cards:
                self.alive_cards[character] = False
            
            # Update our hand
            for card in event["info"]["players"][me]["cards"]:
                if card["character"] is None:
                    raise Exception("accessed someone else's cards! Bad logic!")
                if card["alive"]:
                    self.alive_cards[card["character"]] = True

    def decide_action(self, options):
        possible_actions = possible_responses(options)

        # If we can coup, then coup
        if can_coup(options):
            return coup(random.choice(coup_targets(options)))
        
        # Randomly select a character that we have to do an action with, if possible
        for character in random.sample(list(self.alive_cards), len(self.alive_cards)):
            if self.alive_cards[character]:
                for action in characters_to_moves[character]["action"]:
                    if action in possible_actions:
                        if requires_target(action):
                            return convert(action, random.choice(options[action]))
                        else:
                            return convert(action)

        # Otherwise, let's randomly decide between income and foreign aid
        if random.random() < 0.5:
            return income()
        else:
            return foreign_aid()

    def decide_reaction(self, options):
        for character in options["Block"]:
            if self.alive_cards[character]:
                return block(character) 
        if options["Challenge"] and random.random() < 0.25:
            return challenge() 
        return decline()

    def decide_card(self, options):
        return random.choice(options)

    def decide_exchange(self, options):
        return choose_exchange_cards(random.sample(options["cards"].keys(), options["n"]))


if __name__ == "__main__":
    start(HonestAgent(), sys.argv[1])
