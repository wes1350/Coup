import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Customize game settings.")
    # Engine config
    parser.add_argument("-n", "--n_players", type=int, help="Number of players")
    parser.add_argument("-cp", "--cards_per_player", type=int, help="Number of cards each player starts with")
    parser.add_argument("-cc", "--cards_per_character", type=int, help="How many cards of each character type are in the deck")
    parser.add_argument("-sc", "--starting_coins", type=int, help="How many coins each player starts with")
    parser.add_argument("-p", "--penalize_p1_in_2p_game", type=bool, help="Penalize the first player in a two person game by deducting coins at the start")
    parser.add_argument("-pa", "--first_player_coin_penalty", type=int, help="How many coins to penalize the first player in a two person game")
    parser.add_argument("-m", "--reaction_choice_mode", type=str, choices=["first", "random", "first_block", "first_challenge", "random_block", "random_challenge"], help="How to prioritize reactions when there are multiple")
    parser.add_argument("-ct", "--mandatory_coup_threshold", type=int, help="How many coins a player starts a turn with that obligates them to coup on that turn.")
    parser.add_argument("-ne", "--n_cards_for_exchange", type=int, help="How many cards a player draws during an Exchange.")
    parser.add_argument("-s", "--engine_sleep_duration", type=float, help="How long Engine sleeps when waiting for a response")

    # app config
    parser.add_argument("-k", "--keep_client_order", action="store_true", help="Don't randomize client order")

    args = parser.parse_args()
    specified_args = {k: v for k, v in vars(args).items() if v is not None}
    return specified_args
