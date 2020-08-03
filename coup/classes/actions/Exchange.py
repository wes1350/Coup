from .Action import Action

class Exchange(Action):
    aliases = ["exchange", "e"]
    
    def __init__(self):
        super().__init__(as_character="Ambassador", exchange_with_deck=True)

    def output_rep(self) -> str:
        return "Exchanges their hand"

    def __str__(self) -> str:
        return "Exchange"
