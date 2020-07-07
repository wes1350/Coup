"""An Agent that always takes Income unless forced to Coup, and that never Blocks or Challenges."""

if __name__ == "__main__":
    from utils.game import *
    from utils.responses import *
    from utils.network import *
else:
    from .utils.game import *
    from .utils.responses import *
    from .utils.network import *

def decide_action(options):
    if can_income(options):
        return income()
    else:
        targets = coup_targets(options)
        if targets:
            return coup(targets[0])
        # Should always be able to Income unless we are forced to Coup
        assert False

def decide_reaction(options):
    return decline()

def decide_card(options):
    return options[0]


if __name__ == "__main__":
    start(on_action=decide_action, on_reaction=decide_reaction, on_card=decide_card)
