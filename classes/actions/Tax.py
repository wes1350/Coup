from .Action import Action

class Tax(Action):
    def __init__(self):
        super().__init__(cost=-3, as_character="Duke")
