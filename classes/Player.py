"""A class representing a player and their state, including cards and coin balance."""
from .Card import Card

class Player:
    def __init__(self, id_ : int, coins : int, cards : list):
        self._id = id_
        self._coins = coins
        self._cards = cards
    
    def get_id(self) -> int:
        return self._id

    def get_coins(self) -> int:
        return self._coins

    def change_coins(self, change : int):
        """Given a requested change, add the requested number of coins to the player's balance. If the resulting balance would be negative, set it to 0."""
        self._coins = max(self._coins + change, 0)
    
    def get_cards(self) -> list:
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
        
    def __str__(self):
        rep = "\nPlayer {}: {} coins, {}".format(self._id, self._coins, ", ".join([c.__str__() for c in self._cards])) 
        return rep
