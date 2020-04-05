from typing import Callable
from State import State
from Action import Action

class Character:
    def influence(self) -> Callable[[State], State]:
        pass
    
    """  """
    def counter(self, action: Action) -> bool:
        pass