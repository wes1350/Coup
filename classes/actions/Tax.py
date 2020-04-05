from .Action import Action

class Tax(Action):
    def __init__(self):
        super.__init__("cost": -3, "take_coins_target_id"=-1)
