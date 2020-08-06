from .Character import Character

class Duke(Character):

    def __init__(self):
        pass

    def description(self):
        return "Dukes can do the following:\n    Tax: Take 3 coins from the Treasury.\n    Block: Foreign Aid"

    def __str__(self):
        return "Duke"
