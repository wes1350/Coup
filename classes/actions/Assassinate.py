from .Action import Action

class Assassinate(Action):
    def __init__(self, target, card_id):
        super().__init__(kill=True, target=target, kill_card_id=card_id, cost=3)
