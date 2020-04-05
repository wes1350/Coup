from Character import Character

class Card:
    def __init__(self, character : Character) -> None:
        self.character = character
        self.face_up = False

    def get_character(self) -> Character:
        return self.character