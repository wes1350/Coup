import random
if __name__ == "__main__":
    from Card import Card
    from Characters import Ambassador, Assassin, Captain, Contessa, Duke
else:
    from .Card import Card
    from .characters import Ambassador, Assassin, Captain, Contessa, Duke

class Deck:
    """Class for managing the Coup deck. The deck only contains information about the cards it contains, and whether a card has been dealt (assigned) or not. It does not know about player assignments.To interact with the deck, we call methods such as draw."""
    ALL_CHARACTERS = [Ambassador.Ambassador, Assassin.Assassin, Captain.Captain, Contessa.Contessa, Duke.Duke]

    def __init__(self, n_players : int, n_cards_per_character : int) -> None:
        ids = [i for i in range(n_cards_per_character * len(Deck.ALL_CHARACTERS))]
        self._deck = {}
        for char in Deck.ALL_CHARACTERS:
            for _ in range(n_cards_per_character):
                # random id
                id_ = ids.pop(random.randint(1, len(ids)) - 1)
                self._deck[id_] = Card(character=char(), id_=id_)

    def draw(self, n : int) -> list:
        unassigned = [card for card in self._deck if not self._deck[card].is_assigned()]
        if n <= 0:
            raise ValueError("Must draw more than 0 cards")
        if n > len(unassigned):
            raise ValueError("Cannot draw {} cards when only {} are in the deck".format(n, len(unassigned)))
        selected_cards = random.sample(unassigned, n)
        for id_ in selected_cards:
            self._deck[id_].set_assign(True)

        return [self._deck[i] for i in selected_cards]

    def return_card(self, id_ : int) -> None:
        if self._deck.get(id_) is not None:
            self._deck[id_].set_assign(False)
        else:
            raise ValueError("Could not find given card among assigned cards")

    def exchange_card(self, card : Card) -> Card:
        new_card = self.draw(1)[0]
        self.return_card(card.get_id())
        return new_card

    def __str__(self):
        rep = "[\n"
        rep += "\n".join([self._deck[id_].__str__() for id_ in self._deck])
        rep += "]\n"
        return rep
