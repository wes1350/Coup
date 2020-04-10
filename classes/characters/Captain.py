from .Character import Character

class Captain(Character):
    
    def __init__(self):
        pass

    def description(self):
        return "Captains can do the following:\n    Steal: Take 2 coins from another player. If they only have one coin, take only one. (Can be blocked by the Ambassador or the Captain)\n    Block: Steal"


    def __str__(self):
        return "Captain"
