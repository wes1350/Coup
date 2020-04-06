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
        
    def get_character(self) -> Character:
        return self._character

    def get_character_type(self) -> str:
        return str(self.get_character())

    def die(self):
        self._alive = False

    def is_alive(self):
        return self._alive

    def is_assigned(self) -> bool:
        return  self._assigned

    def set_assign(self, value: bool) -> None:
        self._assigned = value

    def get_id(self) -> int:
        return self._id

    def __str__(self):
        rep = "["
        rep += self._character.__str__() + ", "
        rep += ("Alive" if self._alive else "Dead") + ", "
        rep += str(self._id) + "]"
        return rep
