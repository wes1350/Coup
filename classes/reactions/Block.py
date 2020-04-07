from .Reaction import Reaction

class Block(Reaction):
    def __init__(self, player : int, char : str):
        super().__init__(reaction_type="block", from_player=player, as_character=char)
    
