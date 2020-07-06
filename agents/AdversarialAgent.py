"""An Agent that always assassinates, steals, blocks, or challenges given the opportunity."""

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
    if assassinate_targets(options):
        return assassinate(random.choice(options["Assassinate"]))
    elif steal_targets(options):
        return steal(random.choice(options["Steal"]))
    else:
        # Sometimes we can't assassinate because we don't have the coins for it,
        # and we can't steal because nobody else has coins to steal. 
        # In this case we tax.
        return tax()

def decide_reaction(options):
    if can_challenge(options):
        return challenge()
    else:
        return block(random.choice(options["Block"]))

def decide_card(options):
    return random.choice(options)


if __name__ == "__main__":
    start(on_action=decide_action, on_reaction=decide_reaction, 
          on_card=decide_card)
