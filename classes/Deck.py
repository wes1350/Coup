import random
from .Card import Card
from .characters import Ambassador, Assassin, Captain, Contessa, Duke

class Deck:
    """Class for managing the Coup deck. The deck only contains information about the cards it contains, and whether a card has been dealt (assigned) or not. It does not know about player assignments.To interact with the deck, we call methods such as draw."""

    def __init__(self, n_players : int, n_cards_per_character : int) -> None:
        self._deck = []
        for _ in range(n_cards_per_character):
            self._deck.append(Card(character=Ambassador.Ambassador()))
            self._deck.append(Card(character=Assassin.Assassin()))
            self._deck.append(Card(character=Captain.Captain()))
            self._deck.append(Card(character=Contessa.Contessa()))
            self._deck.append(Card(character=Duke.Duke()))
        self._assigned = [False]*len(self._deck)

    def mark_as_assigned(self, assignments : list) -> None:
        for idx in assignments:
            self._assigned[idx] = True
    
    def switch_assignment(self, old : int, new : int) -> None:
        self._assigned[old] = False
        self._assigned[new] = True
    
    def draw(self, n : int, assign : bool = True) -> list:
        unassigned = [i for i in range(len(self._assigned)) if not self._assigned[i]]
        if n <= 0:
            raise ValueError("Must draw more than 0 cards")
        if n > len(unassigned):
            raise ValueError("Cannot draw {} cards when only {} are in the deck".format(n, len(unassigned)))
        selected_cards = random.sample(unassigned, n)
        if assign:
            self.mark_as_assigned(selected_cards)
        return [self._deck[i] for i in selected_cards]

    def return_card(self, card : Card) -> None:
        for i, c in enumerate(self._deck):
            if type(c) == type(card):
                if self.assigned[i]:
                    self.assigned[i] = False
                    return
        raise ValueError("Could not find given card among assigned cards")

    def exchange_card(self, card : Card) -> Card:
        new_card = self.draw(1)
        self.return_card(card)
        return new_card
        
