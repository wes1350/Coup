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

class RandomAgent:
    def __init__(self):
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
    agent = RandomAgent()
    start(on_action=agent.decide_action, on_reaction=agent.decide_reaction, 
          on_card=agent.decide_card, on_exchange=agent.decide_exchange)
