class Config:
    def __init__(self, **kwargs):
        self.n_players = 3
        self.cards_per_player = 2
        self.cards_per_character = 3
        self.starting_coins = 2
        self.penalize_first_player_in_2p_game = True
        self.first_player_coin_penalty = 1

        self.reaction_choice_mode = "random_challenge"

        self.mandatory_coup_threshold = 10

        # initialize other parameters
        for key, value in kwargs.items():
            self.__setattr__(key, value)

