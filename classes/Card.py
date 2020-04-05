from .characters import Character

class Card:
    def __init__(self, character : Character) -> None:
        self.character = character
        self.alive = True

    def get_character(self) -> Character:
        return self.character

    def die(self):
        self.alive = False

    def is_alive(self):
        return self.alive
