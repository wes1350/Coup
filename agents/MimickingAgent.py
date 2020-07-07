"""An Agent that mimics the most recent possible action done by a player."""

import random

if __name__ == "__main__":
    from utils.game import *
    from utils.responses import *
    from utils.network import *
else:
    from .utils.game import *
    from .utils.responses import *
    from .utils.network import *

# Keeps track of a list of actions in the game
state = []

def decide_action(options):
    possible_actions = possible_responses(options)
    if state:
        for i in range(len(state) - 1, -1, -1):
            action = state[i]
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

def update(event):
    if event["event"] == "action":
        state.append(event["info"])
        print("Updating state with action: " + event["info"]["type"])

def decide_reaction(options):
    return decline()

def decide_card(options):
    return random.choice(options)

def decide_exchange(options):
    return choose_exchange_cards(random.sample(options["cards"].keys(), options["n"]))


if __name__ == "__main__":
    start(on_action=decide_action, on_reaction=decide_reaction, 
          on_card=decide_card, on_exchange=decide_exchange, update_f=update)
