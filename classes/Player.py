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
        self._coins = min(self._coins + change, 0)
    
    def get_cards(self) -> list:
        return self._cards

    def set_card(self, i : int, card : Card) -> None:
        self._cards[i] = card 

    def is_eliminated(self) -> bool:
        for card in self._cards:
            if card.is_alive():
                return False
        return True

    def is_alive(self) -> bool:
        return not self.is_eliminated()
        
