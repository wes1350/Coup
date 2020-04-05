from classes.characters import Ambassador, Assassin, Captain, Contessa, Duke
from classes import Card


class Engine:
    CARDS_PER_CHARACTER = 3

    def __init__(self) -> None:
        self.deck = []
        self.initialize_deck()

    def initialize_game(self, n_players : int) -> None:
        self.state = State(n_players)

    def assign_cards_to_players(self, n_players : int) -> dict:
        pass

    def initialize_deck(self) -> None:
        for _ in range(CARDS_PER_CHARACTER):
            self.deck.append(Card(character=Ambassador.Ambassador()))
            self.deck.append(Card(character=Assassin()))
            self.deck.append(Card(character=Captain()))
            self.deck.append(Card(character=Contessa()))
            self.deck.append(Card(character=Duke()))

# Initialize game with n players, create the state object

# while(game is not over):
# - print state
# - query current player for action
# - based on action:
# --- if cannot do reactions:
# ----- execute action
# ----- go to next turn
# --- else (so can do reactions):
# ----- query other players for reactions
# ----- if no reaction:
# ------- execute action
# ----- else (is a reaction):
# ------- among reactions, choose one to use
# ------- if chosen reaction is a challenge:
# --------- settle the challenge
# ------- elif chosen reaction is a block:
# --------- query other players for challenges
# --------- if a challenge is given, choose one among them and settle it 
# - now turn is over, so update game state

# Note: settling a challenge includes executing the original action if the challenge was won by the executor
