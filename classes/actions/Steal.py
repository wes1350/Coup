from .Action import Action

class Steal(Action):
    def __init__(self, target : int, n_coins : int = 2):
        if target is None:
            raise ValueError("Must specify target to steal from")
        super().__init__(steal=True, cost=-1*n_coins, target=target, blockable=True, blockable_by=["Ambassador", "Captain"], actor="Captain")
