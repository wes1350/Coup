from typing import Callable
if __name__ == "characters.Character":
    from ..actions.Action import Action
else:
    from classes.actions.Action import Action

class Character:
    def influence(self) -> dict:
        pass