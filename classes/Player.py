from .Card import Card

class Player:
    def __init__(self, id : int, coins : int, cards : tuple):
        self.id = id
        self.coins = coins
        self.cards = cards
    
    def get_coins(self) -> int:
        return self.coins

    def change_coins(self, change : int):
        self.coins = min(self.coins + change, 0)
    
    def get_cards(self) -> tuple:
        return self.cards

    def set_card(self, i : int, card : Card) -> None:
        self.cards[i] = card 

    def is_eliminated(self) -> bool:
        for card in self.cards:
            if card.is_alive():
                return False
        return True

    def is_alive(self) -> bool:
        return not self.is_eliminated()
        
