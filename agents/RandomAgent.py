"""An Agent that chooses a valid response at random."""

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

class RandomAgent(Agent):
    def __init__(self, verbose=False):
        self.verbose = verbose
        pass

    def decide_action(self, options):
        possible_actions = possible_responses(options)
        action = random.choice(possible_actions)
        if isinstance(options[action], list):
            target = random.choice(options[action])
            return convert(action, target)
        return convert(action)

    def decide_reaction(self, options):
        return self.decide_action(options)

    def decide_card(self, options):
        return random.choice(options)

    def decide_exchange(self, options):
        return choose_exchange_cards(random.sample(options["cards"].keys(), options["n"]))


if __name__ == "__main__":
    start(RandomAgent(), sys.argv[1])
