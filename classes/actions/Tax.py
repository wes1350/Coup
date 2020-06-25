from .Action import Action

class Tax(Action):
    aliases = ["tax", "t"]

    def __init__(self):
        super().__init__(cost=-3, as_character="Duke")

    def output_rep(self) -> str:
        return "Taxes"

    def __str__(self) -> str:
        return "Tax"