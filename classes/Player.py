"""A class representing a player and their state, including cards and coin balance."""
from .Card import Card

from typing import List


class Player:
    def __init__(self, id_ : int, name : str, coins : int, cards : List[Card]) -> None:
        self._id = id_
        self._name = name
        self._coins = coins
        self._cards = cards

    def get_json(self, mask) -> dict:
        player_json = {} 
        player_json['id'] = self._id
        player_json['name'] = self._name
        player_json['coins'] = self._coins
        player_json['cards'] = [card.get_json(mask) for card in self._cards]
        return player_json

    def get_name(self) -> str:
        return self._name
    
    def get_id(self) -> int:
        return self._id

    def get_coins(self) -> int:
        return self._coins

    def change_coins(self, change : int):
        """Given a requested change, add the requested number of coins to the player's balance. If the resulting balance would be negative, set it to 0."""
        self._coins = max(self._coins + change, 0)
    
    def get_cards(self) -> List[Card]:
        return self._cards

    def set_card(self, i : int, card : Card) -> None:
        self._cards[i] = card 

    def kill_card(self, i : int) -> None:
        self._cards[i].die()
    
    def is_eliminated(self) -> bool:
        for card in self._cards:
            if card.is_alive():
                return False
        return True

    def is_alive(self) -> bool:
        return not self.is_eliminated()
        
    def __str__(self) -> str:
        rep = "\nPlayer {}: {} coins, {}".format(self._id, self._coins, ", ".join([str(c) for c in self._cards])) 
        return rep

    def masked_rep(self) -> str:
        rep = "\nPlayer {}: {} coins, {}".format(self._id, self._coins, ", ".join([str(c) if not c.is_alive() else "--Hidden--" for c in self._cards])) 
        return rep
