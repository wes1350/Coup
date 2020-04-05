"""Maintiains the state of a Coup game. The state includes the Deck of cards, the set of players, and the turn state."""

from classes.Player import Player
from classes.Deck import Deck
from classes.Card import Card

class State:

    def __init__(self, n_players : int) -> None:
        self.CARDS_PER_CHARACTER = 3
        # Initialize the deck
        self._deck = Deck(n_players, self.CARDS_PER_CHARACTER)
        # Initialize the players and assign them cards from the deck
        unassigned_cards = self._deck.draw(2 * n_players)
        self._players = []
        for i in range(n_players):
            self._players.append(Player(id=i, coins=2, cards=(unassigned_cards[2*i], unassigned_cards[2*i+1])))

    def get_player_cards(self, id_ : int) -> list:
        return self._players[id_].get_cards()

    def get_player_card(self, player_id : int, card_idx : int) -> Card:
        return self.get_player_cards(player_id)[card_idx]

    def switch_player_card(self, player_id, card_idx) -> None:
        new_card = self._deck.exchange_card(self.get_player_card(player_id, card_idx))  
        self.players.set_card(card_idx, new_card)
