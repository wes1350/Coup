from .Action import Action

class Steal(Action):
    aliases = ["steal", "s"]

    def __init__(self, target : int, n_coins : int = 2):
        if target is None:
            raise ValueError("Must specify target to steal from")
        super().__init__(steal=True, cost=-1*n_coins, target=target, blockable=True, blockable_by=["Ambassador", "Captain"], as_character="Captain")

    def output_rep(self) -> str:
        return "Steals from Player {}".format(self.target)
