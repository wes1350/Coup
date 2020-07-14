"""An Agent that always takes Income unless forced to Coup, and that never Blocks or Challenges."""

if __name__ == "__main__":
    from utils.game import *
    from utils.responses import *
    from utils.network import *
    from Agent import Agent
else:
    from .utils.game import *
    from .utils.responses import *
    from .utils.network import *
    from .Agent import Agent

class IncomeAgent(Agent):
    def __init__(self):
        pass

    def decide_action(self, options):
        if can_income(options):
            return income()
        else:
            targets = coup_targets(options)
            if targets:
                return coup(targets[0])
            # Should always be able to Income unless we are forced to Coup
            assert False

    def decide_reaction(self, options):
        return decline()

    def decide_card(self, options):
        return options[0]


if __name__ == "__main__":
    start(IncomeAgent())
