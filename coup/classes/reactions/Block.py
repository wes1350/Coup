from .Reaction import Reaction

class Block(Reaction):
    aliases = ["block", "b"]

    def __init__(self, from_player : int, to_player : int, char : str):
        super().__init__(reaction_type="block", from_player=from_player, to_player=to_player, as_character=char)

