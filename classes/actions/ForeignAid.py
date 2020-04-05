from .Action import Action

class ForeignAid(Action):
    def __init__(self):
        super.__init__("cost"=-2, "take_coins_target"=-1)
