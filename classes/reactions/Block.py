from . import Reaction

class Block(Reaction):
    def __init__(self, player : int, char : int):
        super().__init(reaction_type="block", from_player=player, as_character=char)
    