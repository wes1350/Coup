"""An Agent that always assassinates, steals, blocks, or challenges given the opportunity."""

import sys, random

if "." not in __name__:
    from utils.game import *
    from utils.network import *
    from Agent import Agent
else:
    from .utils.game import *
    from .utils.network import *
    from .Agent import Agent

class AdversarialAgent(Agent):
    def __init__(self, verbose=False):
        self.verbose = verbose
        pass

    def decide_action(self, options):
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

    def decide_reaction(self, options):
        if can_challenge(options):
            return challenge()
        else:
            return block(random.choice(options["Block"]))

    def decide_card(self, options):
        return random.choice(options)


if __name__ == "__main__":
    start(AdversarialAgent(), sys.argv[1])
