"""Master class for running Coup. Reads in arguments from the command line, 
   maintains and updates the state, and queries players for actions."""

import random, time, argparse
from typing import List, Optional, Dict, Any

from State import State
from Config import Config
from classes.Card import Card
from classes.actions.Action import Action
from classes.actions.Income import Income
from classes.actions.ForeignAid import ForeignAid
from classes.actions.Tax import Tax
from classes.actions.Steal import Steal
from classes.actions.Assassinate import Assassinate
from classes.actions.Coup import Coup
from classes.actions.Exchange import Exchange
from classes.reactions.Reaction import Reaction
from classes.reactions.Block import Block
from classes.reactions.Challenge import Challenge


class Engine:
    """Maintains all the logic relevant to the game, such as the 
       game state, config, querying players, etc."""

    def __init__(self, args : Dict[str, Any]) -> None:
        """Initialize a new Engine, with arguments from the command line."""
        self._config_status, self._config_err_msg = True, None
        try:
            self.config = Config(**args)
        except ValueError as e:
            self._config_status = False
            self._config_err_msg = getattr(e, 'message', repr(e))
        else:
            self._state = State(self.config)
            print(str(self.config))

    def game_is_over(self) -> bool:
        """Determine if the win condition is satisfied."""
        return self._state.n_players_alive() == 1

    def run_game(self) -> int:
        """Start and run a game until completion, handling game logic as necessary."""
        while not self.game_is_over():
            print(self._state)
            self.play_turn()
            self.next_turn()
        winner = self._state.get_alive_players()[0]
        print("Game is over!\n\nPlayer {} wins!".format(winner))
        return winner

    def play_turn(self) -> None:
        """Play one turn of the game."""
        current_player = self._state.get_current_player_id()
        action = self.query_player_action(current_player)
        target = action.target
        
        if not action.is_blockable() and not action.is_challengeable():
            # Action always goes through, e.g. Income
            self.execute_action(action, current_player, target)
        else:
            # Blocks and/or Challenges are possible. See if anyone decides to challenge
            query_players = [p for p in self._state.get_alive_players() if p != current_player]
            reactions = self.query_player_reactions(query_players, action)
            if len(reactions) > 0:
                # At least one player reacted, so handle it
                chosen_reaction = self.choose_among_reactions(reactions)
                reaction_type = chosen_reaction.reaction_type
                if reaction_type == "block":
                    # Handle block reactions
                    blocker = chosen_reaction.from_player
                    query_challenge_players = [p for p in self._state.get_alive_players() 
                                               if p != blocker]
                    challenges = self.query_challenges(query_challenge_players)
                    if len(challenges) > 0:
                        # Someone challenged the block, so resolve the challenge 
                        chosen_challenge = self.choose_among_reactions(challenges)
                        challenger = chosen_challenge.from_player
                        claimed_character = chosen_reaction.as_character
                        losing_player = self._state.get_challenge_loser(claimed_character, 
                                                                        blocker, challenger)
                        card = self.query_player_card(losing_player)
                        self._state.kill_player_card(losing_player, card)
                        if losing_player == blocker:
                            self.execute_action(action, current_player, target, 
                                                ignore_if_dead=True)
                        else:
                            # Enforce any costs to original action executor
                            self.exchange_player_card(blocker, chosen_reaction)
                            self.execute_action(action, current_player, only_pay_cost=True)
                        print("Player {} loses the challenge".format(losing_player))
                    else:
                        # Nobody challenged, so the block is successful
                        # Enforce any costs to original action executor
                        self.execute_action(action, current_player, only_pay_cost=True)
                        print("Action blocked with {}".format(chosen_reaction.as_character))    
                elif reaction_type == "challenge":
                    challenger = chosen_reaction.from_player
                    claimed_character = action.as_character
                    losing_player = self._state.get_challenge_loser(claimed_character, 
                                                                    current_player, challenger)
                    card = self.query_player_card(losing_player)
                    self._state.kill_player_card(losing_player, card)
                    if losing_player == challenger:
                        self.exchange_player_card(current_player, action)
                        self.execute_action(action, current_player, target, ignore_if_dead=True)
                    print("Player {} loses the challenge".format(losing_player))
                else:           
                    raise ValueError("Invalid reaction type encountered")
            else:
                # Nobody reacted, so the action goes through
                self.execute_action(action, current_player, target)   

    def next_turn(self) -> None:
        """Move on to the next turn, updating the game state as necessary."""
        self._state.update_current_player() 

    def choose_among_reactions(self, reactions : List[Reaction]) -> Reaction:
        """Given a list of reactions, return one based on the selection setting."""
        chosen_reaction = None
        mode = self.config.reaction_choice_mode
        if mode == "first":
            chosen_reaction = reactions[0]
        elif mode == "random":
            chosen_reaction = random.choice(reactions)
        elif mode == "first_challenge":
            for reaction in reactions:
                if reaction.reaction_type == "challenge":
                    chosen_reaction = reaction
                    break
                chosen_reaction = reactions[0] 
        elif mode == "first_block":
            for reaction in reactions:
                if reaction.reaction_type == "block":
                    chosen_reaction = reaction
                    break
                chosen_reaction = reactions[0] 
        elif mode == "random_challenge":
                desired = [r for r in reactions if r.reaction_type == "challenge"]
                if len(desired) > 0:
                    chosen_reaction = random.choice(desired)
                else:
                    chosen_reaction = random.choice(reactions)
        elif mode == "random_block":
                desired = [r for r in reactions if r.reaction_type == "block"]
                if len(desired) > 0:
                    chosen_reaction = random.choice(desired)
                else:
                    chosen_reaction = random.choice(reactions)
        player = chosen_reaction.from_player
        reaction_type = chosen_reaction.reaction_type
        is_block = reaction_type == "block"
        character = chosen_reaction.as_character if is_block else None
        print("Player {} does a {}{}".format(player, reaction_type, " as {}".format(character) if is_block else ""))
        return chosen_reaction

    def execute_action(self, action: Action = None, source : int = None, target : int = None, ignore_if_dead : bool = False, only_pay_cost : bool = False) -> None:
        """Given an action, execute it based on the parameters provided."""
        ignore_killing = False
        if not only_pay_cost:
            # Query affected player if necessary
            if not action.ready():
                card = self.query_player_card(target, ignore_if_dead)
                if card is not None:
                    action.kill_card_id = card
                else:   
                    # card is None because the player is already dead and there is no card to choose
                    ignore_killing = True
        self._state.execute_action(source, action, ignore_killing, only_pay_cost)

    def query_player_action(self, player_id : int) -> Action:
        """Given a player, query them for an action, validating it and reprompting as necessary."""
        # First, check if the player has 10 coins and is forced to coup
        if self._state.player_must_coup(player_id):
            return self.query_player_coup_target(player_id)
        else:
            player_balance = self._state.get_player_balance(player_id)
            can_coup = player_balance >= Coup().cost
            can_assassinate = player_balance >= Assassinate().cost
            while True:
                query_msg = ("Player {}, what is your action?\n"
                             "You can: [I]ncome  [F]oreign Aid  [T]ax  [S]teal  [E]xchange"
                            .format(player_id))
                if can_assassinate:
                    query_msg += "  [A]ssassinate"
                if can_coup:
                    query_msg += "  [C]oup"
                
                response = input(query_msg + "\n")
                try: 
                    action = self.translate_action_choice(response)
                except ValueError:
                    print("Invalid action, please try again.")
                else:
                    valid = self.validate_action(action, player_id)
                    if valid:
                        return action
                    print("Impossible action, please try again.")
                    

    def query_player_reactions(self, players : List[int], action : Action) -> List[Reaction]:
        """Given an action and a list of players to query, prompt players for reactions"""
        reactions = []
        target = action.target
        for player_id in players:
            while True:
                if target is not None:
                    if target == player_id:
                        message_action = "[B]lock or [C]hallenge"
                    else:
                        message_action = "[C]hallenge"
                else:
                    challengeable = action.as_character 
                    blockable = action.is_blockable()
                    if challengeable and blockable:
                        message_action = "[B]lock or [C]hallenge"
                    elif challengeable:
                        message_action = "[C]hallenge"
                    elif blockable:
                        message_action = "[B]lock"
                    else:
                        raise ValueError("Should not ask for reaction to unreactionable action")
                response = input("Player {}, are you going to {}?\n".format(player_id, message_action))
                try: 
                    reaction = self.translate_reaction_choice(response, player_id, action)
                except ValueError:
                    print("Invalid reaction, please try again.")
                else:
                    if reaction is None:
                        break
                    valid = self.validate_reaction(reaction, action)
                    if valid:
                        reactions.append(reaction)
                        break
                    print("Impossible reaction, please try again.")
        return reactions

    def query_challenges(self, players : List[int]) -> List[Challenge]:
        """Given a list of players to query, ask them if they want to challenge."""
        challenges = []
        for player_id in players:
            while True:
                response = input("Player {}, are you going to [C]hallenge?\n".format(player_id))
                try: 
                    reaction = self.translate_challenge_answer(response, player_id)
                    if reaction is not None:
                        challenges.append(reaction)
                    break
                except ValueError:
                    print("Invalid response, please try again.")
        return challenges

    def query_player_coup_target(self, player_id : int) -> int:
        """Given a player who must coup, ask them who they are going to coup."""
        while True:
            response = input("Player {}, who are you going to coup?\n".format(player_id))
            try:
                action = self.translate_coup_target(response)
            except ValueError:
                print("Invalid coup target, please try again.")
            else:
                valid = self.validate_action(action, player_id)
                if valid:
                    return action
                print("Invalid coup target, please try again.")
            

    def query_player_card(self, player_id : int, ignore_if_dead : bool = False) -> int:
        """Given a player who must choose a card to discard, query them for their card choice."""
        # First, determine whether we need to query the player for a card
        options = self._state.get_player_living_card_ids(player_id)
        if len(options) == 0:
            if ignore_if_dead:
                return None
            else:
                raise ValueError("Cannot choose a card from a Player who is eliminated")
        elif len(options) == 1:
            return options[0]
        else:
            while True:
                response = input("Player {}, one of your characters must die. Which one do you pick?\n".format(player_id))
                try:
                    card = self.translate_card_choice(response, options)
                    return card
                except ValueError:
                    print("Invalid card, please try again.")

    def translate_action_choice(self, response : str) -> Action:
        """Given an action response, translate it appropriately"""
        response = response.strip().lower()
        args = response.split(" ")
        action_name = args[0]
        target = None if len(args) == 1 else int(args[1])
     
        if action_name in ["i", "income"]:
            return Income()
        elif action_name in ["f", "foreignaid", "foreign aid"]:
            return ForeignAid()
        elif action_name in ["t", "tax"]:
            return Tax()
        elif action_name in ["e", "exchange"]:
            return Exchange()
        elif action_name in ["s", "steal"]:
            return Steal(target=target)
        elif action_name in ["a", "assassinate"]:
            return Assassinate(target=target)
        elif action_name in ["c", "coup"]:
            return Coup(target=target)
        else:
            print("ERROR: invalid action name: {}".format(action_name))
            raise ValueError("Invalid action name: {}".format(action_name))

    def translate_reaction_choice(self, response : str, source_id : int, 
                                  action : Action) -> Reaction:
        """Given a reaction response, translate it appropriately."""
        response = response.strip().lower()
        if len(response) == 0:
            return None
        else:
            args = response.split(" ")
            reaction_type = args[0]
            if reaction_type in ["b", "block"]:
                character_options = action.blockable_by
                if len(character_options) == 1:
                    character = character_options[0] 
                    if len(args) > 1:
                        if args[1].lower() != character.lower():
                            raise ValueError("Invalid character choice for block")
                elif len(character_options) > 1:
                    if len(args) != 2:
                        raise ValueError("Invalid number of arguments for block")
                    character = args[1]
                    if character not in [c.lower() for c in character_options]:  
                        raise ValueError("Invalid character choice for block")
                return Block(source_id, character.capitalize())
            elif reaction_type in ["c", "challenge"]:
                return Challenge(source_id)
            else:
                raise ValueError("Invalid reaction type")

    def translate_challenge_answer(self, response : str, source_id : int) -> Challenge:
        """Given a challenge response, translate it appropriately."""
        response = response.strip().lower()
        if len(response) == 0 or response in ["no", "n"]:  
            return None
        elif response in ["challenge", "c", "yes", "y"]:
            return Challenge(source_id)
        else:
            raise ValueError("Invalid challenge answer")

    def translate_coup_target(self, response : str) -> Action:
        response = response.strip()
        """Given a coup target response, translate it appropriately."""
        target = int(response)
        return Coup(target=target)

    def translate_card_choice(self, response : str, options : List[int]) -> int:
        response = response.strip()
        """Given a card choice to discard, translate it appropriately."""
        chosen_card = int(response)
        if chosen_card not in options:
            print("ERROR: invalid card number: {}".format(chosen_card))
            raise ValueError("Invalid card option") 
        return chosen_card       

    def validate_action(self, action : Action, player_id : int) -> bool:
        """Given an action, return whether it can be done given the current state."""
        return self._state.validate_action(action, player_id) 

    def validate_reaction(self, reaction : Reaction, action : Action) -> bool:
        """Given a reaction, return whether it can be done given the turn state."""
        reaction_type = reaction.reaction_type
        if reaction_type == "block":
            target = action.target
            if target is not None:
                reactor = reaction.from_player
                if target != reactor:
                    print("Cannot block action when not the target")
                    return False
            if not action.is_blockable():
                print("Action is unblockable")
                return False
            character = reaction.as_character
            blockable_by = action.blockable_by
            if character not in blockable_by:
                print("Specified character cannot block this action")
                return False
            return True
        elif reaction_type == "challenge":
            if not action.is_challengeable():
                print("Action cannot be challenged")
                return False
            return True
        else:
            return False

    def exchange_player_card(self, player : int, move : Reaction) -> None:
        """Given a player and an action or reaction they did, exchange one of their cards appropriately. This is called when a player wins a challenge and needs to replace the challenged character."""
        character = move.as_character
        self._state.exchange_player_card(player, character)

    def get_config_status(self):
        return self._config_status
    
    def get_config_err_msg(self):
        return self._config_err_msg


def parse_args():
    parser = argparse.ArgumentParser(description="Customize game settings.")
    parser.add_argument("-n", "--n_players", type=int, help="Number of players")
    parser.add_argument("-cp", "--cards_per_player", type=int, help="Number of cards each player starts with")
    parser.add_argument("-cc", "--cards_per_character", type=int, help="How many cards of each character type are in the deck")
    parser.add_argument("-s", "--starting_coins", type=int, help="How many coins each player starts with")
    parser.add_argument("-p", "--penalize_p1_in_2p_game", type=bool, help="Penalize the first player in a two person game by deducting coins at the start")
    parser.add_argument("-pa", "--first_player_coin_penalty", type=int, help="How many coins to penalize the first player in a two person game")
    parser.add_argument("-m", "--reaction_choice_mode", type=str, choices=["first", "random", "first_block", "first_challenge", "random_block", "random_challenge"], help="How to prioritize reactions when there are multiple")
    parser.add_argument("-ct", "--mandatory_coup_threshold", type=int, help="How many coins a player starts a turn with that obligates them to coup on that turn.")
    parser.add_argument("-ne", "--n_cards_for_exchange", type=int, help="How many cards a player draws during an Exchange.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    specified_args = {k: v for k, v in vars(args).items() if v is not None}
    engine = Engine(specified_args)
    if not engine.get_config_status():
        print("\nInvalid configuration: " + engine.get_config_err_msg().split("'")[1])
        print("\nCannot run game; exiting.")
    else:
        winner = engine.run_game()
