from .Action import Action

class Coup(Action):
    def __init__(self, player_id, card_id):
        super.__init__("kill"=True, "target"=player_id, "kill_card_id"=card_id, "cost"=7)
