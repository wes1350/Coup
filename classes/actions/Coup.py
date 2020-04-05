from .Action import Action

class Coup(Action):
    def __init__(self, target, card_id):
        super().__init__(kill=True, target=target, kill_card_id=card_id, cost=7)
