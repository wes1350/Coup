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

class MimickingAgent(Agent):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.action_queue = []

    def decide_action(self, options):
        possible_actions = possible_responses(options)
        if self.action_queue:
            for i in range(len(self.action_queue) - 1, -1, -1):
                action = self.action_queue[i]
                target = action["target"]
                name = action["type"]
                if name in possible_actions:
                    if target is not None:
                        possible_targets = options[name]
                        # Try to use the same target
                        if target in possible_targets:
                            return convert(name, target)
                        else:
                            return convert(name, random.choice(possible_targets))
                    else:
                        return convert(name)
            # Couldn't mimic any previous actions. Let's try to coup, and
            # if that isn't possible, just take income
            if coup_targets(options):
                target = random.choice(options["Coup"])
                return coup(target)
            return income()
        else:
            # We are first to go in the game, might as well tax
            return tax()

    def update(self, event):
        if event["event"] == "action":
            self.action_queue.append(event["info"])
            print("Updating state with action: " + event["info"]["type"])

    def decide_reaction(self, options):
        return decline()

    def decide_card(self, options):
        return random.choice(options)

    def decide_exchange(self, options):
        return choose_exchange_cards(random.sample(options["cards"].keys(), options["n"]))


if __name__ == "__main__":
    start(MimickingAgent(), sys.argv[1])
