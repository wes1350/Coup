from .Action import Action

class ForeignAid(Action):
    aliases = ["foreign aid", "foreignaid", "f"]

    def __init__(self):
        super().__init__(cost=-2, blockable=True, blockable_by=["Duke"])

    def output_rep(self) -> str:
        return "takes Foreign Aid"

    def __str__(self) -> str:
        return "ForeignAid"
