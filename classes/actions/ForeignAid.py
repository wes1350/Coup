from .Action import Action

class ForeignAid(Action):
    def __init__(self):
        super().__init__(cost=-2, blockable=True, blockable_by=["Duke"])
