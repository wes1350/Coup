from .Action import Action

class Assassinate(Action):
    aliases = ["assassinate", "a"]

    def __init__(self, target : int, card_id : int = None):
        super().__init__(kill=True, target=target, kill_card_id=card_id, cost=3, blockable=True, blockable_by=["Contessa"], as_character="Assassin", pay_when_unsuccessful=True)

    def ready(self):
        return self.kill_card_id is not None and self.target is not None

    def output_rep(self) -> str:
        return "Assassinates Player {}".format(self.target)

    def __str__(self) -> str:
        return "Assassinate"