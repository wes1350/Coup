from .Action import Action

class Steal(Action):
    def __init__(self, target, n_coins=2):
        if target == -1:
            raise ValueError("Cannot steal from the bank")
        super().__init__(steal=True, cost=-1*n_coins, target=target)
