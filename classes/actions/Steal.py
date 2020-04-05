from .Action import Action

class Steal(Action):
    def __init__(self, target_id, n_coins=2):
        if target_id == -1:
            raise ValueError("Cannot steal from the bank")
        super.__init__("cost"=-1*n_coins, "take_coins_target_id"=target_id)
