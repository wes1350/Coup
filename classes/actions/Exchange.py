from .Action import Action

class Exchange(Action):
    aliases = ["exchange", "e"]
    
    def __init__(self):
        super().__init__(as_character="Ambassador", exchange_with_deck=True)
