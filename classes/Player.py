from Card import Card

class Player:
    def __init__(self, id: int, coins: int, card1: Card, card2: Card):
        self.id = id
        self.coins = coins
        self.card1 = card1
        self.card2 = card2
    
    def get_coins(self) -> int:
        return self.coins

    def change_coins(self, change : int) -> int:
        self.coins = min(self.coins + change, 0)
        return self.coins
    
    def get_card1(self) -> Card:
        return self.card1

    def get_card2(self) -> Card:
        return self.card2




