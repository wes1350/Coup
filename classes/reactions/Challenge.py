from . import Reaction

class Challenge(Reaction):
    def __init__(self, source : int, target : int):
        super().__init__(reaction_type="challenge", from_player=source, to_player=target)
