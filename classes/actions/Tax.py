from .Action import Action

class Tax(Action):
    def __init__(self):
        super.__init__("cost": -3, "target"=-1)
