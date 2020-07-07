"""An Agent that chooses a valid response at random."""

import random

if __name__ == "__main__":
    from utils.game import *
    from utils.responses import *
    from utils.network import *
else:
    from .utils.game import *
    from .utils.responses import *
    from .utils.network import *

def decide_action(options):
    possible_actions = possible_responses(options)
    action = random.choice(possible_actions)
    if isinstance(options[action], list):
        target = random.choice(options[action])
        return convert(action, target)
    return convert(action)

def decide_reaction(options):
    return decide_action(options)

def decide_card(options):
    return random.choice(options)

def decide_exchange(options):
    return choose_exchange_cards(random.sample(options["cards"].keys(), options["n"]))


if __name__ == "__main__":
    start(on_action=decide_action, on_reaction=decide_reaction, 
          on_card=decide_card, on_exchange=decide_exchange)
