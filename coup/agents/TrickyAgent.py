"""An Agent that mimics the most recent possible action done by a player."""

import sys, random

if "." not in __name__:
    from utils.game import *
    from utils.network import *
    from Agent import Agent
    from HonestAgent import HonestAgent
    from RandomAgent import RandomAgent
else:
    from .utils.game import *
    from .utils.network import *
    from .Agent import Agent
    from .HonestAgent import HonestAgent
    from .RandomAgent import RandomAgent


class TrickyAgent(Agent):
    def __init__(self, honesty=0.5, **kwargs):
        super().__init__(**kwargs)
        self.honest_agent = HonestAgent()
        self.random_agent = RandomAgent()
        self.honesty = honesty
        self.tag = str(round(100*honesty))

    def update(self, event):
        self.honest_agent.update(event)

    def decide_action(self, options):
        if random.random() < self.honesty:
            return self.honest_agent.decide_action(options)
        else:
            return self.random_agent.decide_action(options)

    def decide_reaction(self, options):
        if random.random() < self.honesty:
            return self.honest_agent.decide_reaction(options)
        else:
            return self.random_agent.decide_reaction(options)

    def decide_card(self, options):
        return random.choice(options)

    def decide_exchange(self, options):
        return choose_exchange_cards(random.sample(options["cards"].keys(), options["n"]))


if __name__ == "__main__":
    start(TrickyAgent(), sys.argv[1])
