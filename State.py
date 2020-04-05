from classes.Player import Player
from classes.Deck import Deck

class State:

    def __init__(self, n_players : int, card_assignments : dict) -> None:
        self._deck = Deck(n_players)
        self.players = []
        for i in range(n_players):
            self.players.append(Player(id=i, coins=2, ))
