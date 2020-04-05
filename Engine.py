import random
from classes.Card import Card
from State import State

class Engine:

    def __init__(self) -> None:
        self.state = State(n_players=3)

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

if __name__ == "__main__":
    Engine()