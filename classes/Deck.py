import random
from .Card import Card
from .characters import Ambassador, Assassin, Captain, Contessa, Duke

class Deck:

    def __init__(self, n_players, n_cards_per_character):
        self._deck = []
        for _ in range(n_cards_per_character):
            self._deck.append(Card(character=Ambassador.Ambassador()))
            self._deck.append(Card(character=Assassin.Assassin()))
            self._deck.append(Card(character=Captain.Captain()))
            self._deck.append(Card(character=Contessa.Contessa()))
            self._deck.append(Card(character=Duke.Duke()))
        random.shuffle(self._deck)
        self.assignments = self._assign_cards_to_players(n_players)

        def _assign_cards_to_players(self, n_players : int) -> dict:
            assignments = {}
            for i in range(n_players):
                assignments[i] = (2*i, 2*i+1)
            return assignments

        def get_player_cards(self, id_):
            return (self._deck[self.assignments[0]], self._deck[self.assignments[1]])

        def _get_unassigned_indices(self) -> list:
            assigned = []
            for id_ in self.assignments:
                assigned.append([x for x in self.assignments[id_]])
            unassigned = []
            for i in range(len(self._deck)):
                if i not in assigned:
                    unassigned.append(i)
            return unassigned    
                
        def _draw_unassigned_cards(self, n : int):
            unassigned = self._get_unassigned_indices()
            if n <= 0:
                raise ValueError("Must draw more than 0 cards")
            if n > len(unassigned):
                raise ValueError("Cannot draw {} cards when only {} are in the deck".format(n, len(unassigned)))
            selected_cards = random.sample(unassigned)
            return selected_cards
