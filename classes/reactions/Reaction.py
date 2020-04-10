"""The base class for Reactions, which are made to counter an Action."""

class Reaction:
    def __init__(self, **kwargs):
        reaction_type = None
        from_player = None

        for arg in kwargs:
            self.__setattr__(arg, kwargs[arg])
