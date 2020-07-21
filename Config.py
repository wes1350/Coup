"""Maintains various parameters used in the game, such as the number of players and number of coins per player."""

from typing import NoReturn
from agents import *

class Config:
    """The class storing all the config parameters."""
    def __init__(self, **kwargs) -> None:
#         self.local_ais = {}
#         self.local_ais = {0: IncomeAgent(), 1: RandomAgent(), 2: AdversarialAgent(), 3: MimickingAgent()}
        self.local_ais = {0: KerasAgent(None, debug=False), 
                           1: IncomeAgent()}

        self.n_players = 2 if not self.local_ais else len(self.local_ais)
        self.cards_per_player = 2
        self.cards_per_character = 3
        self.starting_coins = 2
        self.penalize_first_player_in_2p_game = True
        self.first_player_coin_penalty = 1

        self.reaction_choice_mode = "random_challenge"

        self.mandatory_coup_threshold = 10

        self.n_cards_for_exchange = 2

        self.pay_on_successful_challenges = False

        self.engine_sleep_duration = 0.5 

        # Set initial hands for each player
        self.starting_hands = None
        # self.starting_hands = {0: ["Duke", "Captain"],
        #                        1: ["Assassin", "Contessa"],
        #                        2: ["Captain", "Captain"]}

        # Set deck characters
        self.deck_configuration = None
#         self.deck_configuration = {"Ambassador": 0,
#                                    "Assassin": 0,
#                                    "Captain": 2, 
#                                    "Contessa": 0, 
#                                    "Duke": 4}

        # initialize other parameters
        for key, value in kwargs.items():
            self.__setattr__(key, value)

        self.validate_args()

    def validate_args(self) -> NoReturn:
        """Ensure that the starting arguments give a valid configuration."""
        
        # Make sure that there are enough cards in the deck for the settings
        max_cards_in_use = self.n_players * self.cards_per_player + self.n_cards_for_exchange
        cards_in_deck = self.cards_per_character * 5
        if max_cards_in_use > cards_in_deck:
            raise ValueError("Not enough cards to play given game settings")
        
        # Ensure first player penalty in 2p games is not greater than starting coins
        if self.n_players == 2 and self.penalize_first_player_in_2p_game:
            if self.first_player_coin_penalty > self.starting_coins:
                raise ValueError("First player penalty is greater than number of starting coins")
        
        # Ensure reaction choice mode is valid
        if self.reaction_choice_mode not in ["first", "random", "first_block", "first_challenge", "random_block", "random_challenge"]:
            raise ValueError("Invalid reaction choice mode: {}".format(self.reaction_choice_mode))

        # Ensure starting hand configuration is valid
        # Ensure all hands have the same length
        if self.starting_hands:
            assert len(set([len(self.starting_hands[i]) for i in self.starting_hands])) == 1
            assert self.n_players == len(self.starting_hands)

    def __str__(self) -> str:
        """Nicely print all the game settings."""
        rep = "\nGame settings:\n\n"
        settings = vars(self)
        for v in settings:
            rep += "{}: {}\n".format(v, settings[v])
        return rep
