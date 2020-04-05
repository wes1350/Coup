from Player import Player
class State:

    def __init__(self, n_players : int, card_assignments : dict) -> None:
        self.players = []
        for i in range(n_players):
            self.players.append(Player(id=i, coins=2, ))