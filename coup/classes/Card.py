"""A class representing a card in a player's hand or in the deck."""

if __name__ == "Card":
    from characters import Character
else:
    from .characters import Character

class Card:
    def __init__(self, character: Character, id_: int, assigned: bool = False) -> None:
        self._character = character
        self._alive = True
        self._assigned = assigned
        self._id = id_

    def get_json(self, mask : bool) -> dict:
        return {'character': None if self._alive and mask else self.get_character_type(), "alive": self._alive}
        
    def get_character(self) -> Character:
        return self._character

    def get_character_type(self) -> str:
        """Return character type, e.g. Contessa."""
        return str(self.get_character())

    def die(self):
        self._alive = False

    def is_alive(self) -> bool:
        return self._alive

    def is_assigned(self) -> bool:
        """Return whether the card has been marked as in a player's hand, or is unassigned in the deck."""
        return self._assigned

    def set_assign(self, value: bool) -> None:
        self._assigned = value

    def get_id(self) -> int:
        return self._id

    def __str__(self) -> str:
        rep = "["
        rep += str(self._character) + ", "
        rep += ("Alive" if self._alive else "Dead") + "]"
        return rep
