class Action:
    aliases = None

    def __init__(self, **kwargs):
        self.from_player = None
        self.target = None
        self.steal = False
        self.kill = False
        self.kill_card_id = None
        self.as_character = None  # what card we are claiming e.g. Duke for Tax
        self.cost = 0
        self.blockable = False
        self.blockable_by = None
        self.pay_when_unsuccessful = False
        self.exchange_with_deck = False

        for arg in kwargs:
            self.__setattr__(arg, kwargs[arg])

    def is_blockable(self):
        return self.blockable

    def is_challengeable(self):
        return self.as_character is not None

    def ready(self) -> bool:
        return True

    def history_rep(self) -> dict:
        return {"type": str(self), "as_character": self.as_character, "from_player": self.from_player, "target": self.target}

    def output_rep(self) -> str:
        return None

    def set_source(self, source_id : int) -> None:
        self.__setattr__("from_player", source_id)
