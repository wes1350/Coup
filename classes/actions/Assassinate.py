from .Action import Action

class Assassinate(Action):
    def __init__(self, target : int, card_id : int = None):
        super().__init__(kill=True, target=target, kill_card_id=card_id, cost=3)

    def set_card_id(self, card_id : int) -> None:
        super().set_property(prop="kill_card_id", value=card_id)

    def ready(self):
        return self.get_property("kill_card_id") is not None
