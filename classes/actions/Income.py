from .Action import Action

class Income(Action):
    aliases = ["income", "i"]

    def __init__(self):
        super().__init__(cost=-1)

    def output_rep(self) -> str:
        return "takes Income"
