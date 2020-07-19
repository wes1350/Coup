"""The base class for Reactions, which are made to counter an Action."""

class Reaction:
    def __init__(self, **kwargs):
        self.reaction_type = None
        self.from_player = None
        self.to_player = None
        self.as_character = None

        for arg in kwargs:
            self.__setattr__(arg, kwargs[arg])

    def history_rep(self) -> dict:
        return {"type": self.reaction_type, "from": self.from_player, "to": self.to_player, "as_character": self.as_character}
