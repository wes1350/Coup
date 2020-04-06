"""Maintiains the state of a Coup game. The state includes the Deck of cards, the set of players, and the turn state."""

from classes.Player import Player
from classes.Deck import Deck
from classes.Card import Card
from classes.actions.Action import Action

class State:

    def __init__(self, n_players : int) -> None:
        self._n_players = n_players
        self.CARDS_PER_CHARACTER = 3
        # Initialize the deck
        self._deck = Deck(n_players, self.CARDS_PER_CHARACTER)
        # Initialize the players and assign them cards from the deck
        unassigned_cards = self._deck.draw(2 * n_players)
        self._players = []
        for i in range(n_players):
            self._players.append(Player(id_=i, coins=2, cards=(unassigned_cards[2*i], unassigned_cards[2*i+1])))

        self._current_player_id = 0
        # Initialize the current turn
        self._current_turn = []

    def get_current_player_id(self) -> int:
        return self._current_player_id

    def update_current_player(self):
        while True:
            self._current_player_id = (self._current_player_id + 1) % self._n_players
            if self.player_is_alive(self._current_player_id):
                break

    def get_player_cards(self, id_ : int) -> list:
        return self._players[id_].get_cards()

    def get_player_card(self, player_id : int, card_idx : int) -> Card:
        return self.get_player_cards(player_id)[card_idx]

    def get_player_living_card_ids(self, player_id : int) -> list:
        cards = self.get_player_cards(player_id)
        chosen_cards = []
        for i, card in enumerate(cards):
            if card.is_alive():
                chosen_cards.append(i)
        return chosen_cards

    def switch_player_card(self, player_id, card_idx) -> None:
        new_card = self._deck.exchange_card(self.get_player_card(player_id, card_idx))  
        self.players.set_card(card_idx, new_card)

    def player_is_alive(self, id_ : int) -> bool:
        return self._players[id_].is_alive()

    def n_players_alive(self) -> bool:
        statuses = [self.player_is_alive(i) for i in range(self._n_players)]
        return sum([1 for x in statuses if x])
    
    def get_alive_players(self) -> list:
        return [self._players[i].get_id() for i in range(self._n_players) if self.player_is_alive(i)]

    def execute_action(self, player : int, action : Action) -> None:
        target = action.get_property("target")

        # Handle coin balances
        cost = action.get_property("cost")        
        self._players[player].change_coins(-1 * cost)
        if action.get_property("steal"):
            self._players[target].change_coins(cost)

        # Handle assassinations
        if action.get_property("kill"):
            card_id = action.get_property("kill_card_id")
            self._players[target].kill_card(card_id)

    def validate_action(self, action : Action, player_id : int) -> bool:
        # Validate the cost 
        budget = self._players[player_id].get_coins()
        if action.get_property("cost") > budget:
            return False
        
        # Validate the target, if applicable
        has_target = action.get_property("target") is not None
        if has_target:
            target_id = action.get_property("target") 
            if not self.player_is_alive(target_id):
                return False
        
        return True

    def __str__(self):
        rep = "Deck: {}\n".format(self._deck.__str__())
        rep += "Players: [{}]\n\n".format("".join([p.__str__() for p in self._players]))
        rep += "Current Player: {}\n".format(self._current_player_id)
        
        return rep
