from .Reaction import Reaction

class Challenge(Reaction):
    def __init__(self, source : int):
        super().__init__(reaction_type="challenge", from_player=source)
