from .Character import Character

class Ambassador(Character):

    def __init__(self):
        pass

    def description(self) -> str:
        return "Ambassadors can do the following:\n    Exchange: Exchange cards with the Court. First take random cards (default: 2) from the Court deck. Choose which, if any, to exchange with your face-down cards. Then return two cards to the Court deck. \n    Block: Steal"

    def __str__(self):
        return "Ambassador"
