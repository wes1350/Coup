from .Character import Character

class Assassin(Character):
    
    def __init__(self):
        pass

    def description(self):
        return "Assassins can do the following:\n    Assassinate: Pay 3 coins to the Treasury and launch an assassination against another player. If successful that player immediately loses an influence. (Can be blocked by the Contessa)"

    def __str__(self):
        return "Assassin"
