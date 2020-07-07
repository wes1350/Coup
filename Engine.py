"""Master class for running Coup. Reads in arguments from the command line, 
   maintains and updates the state, and queries players for actions."""

import random, time, sys, os, json
from typing import List, Optional, Dict, Any
from State import State
from Config import Config
from utils.argument_parsing import parse_args
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

    def __init__(self, whisper_f=None, shout_f=None, query_f=None, game_info=None, **kwargs) -> None:
        """Initialize a new Engine, with arguments from the command line."""
        self._config_status, self._config_err_msg = True, None
        self.whisper_f = whisper_f
        self.shout_f = shout_f
        self.query_f = query_f
        try:
            self._config = Config(**kwargs)
        except ValueError as e:
            self._config_status = False
            self._config_err_msg = getattr(e, 'message', repr(e))
            raise ValueError("Invalid Configuration! Terminating.", self._config_err_msg)
        else:
            self.local = None in [self.whisper_f, self.shout_f, self.query_f]
            self._state = State(self._config, self.whisper, self.shout, self.get_response, self.local, game_info.ai_players)
            self.game_info = game_info
            self.game_info.config_settings = str(self._config)
            self.sleep_duration = 0.5

    def game_is_over(self) -> bool:
        """Determine if the win condition is satisfied."""
        return self._state.n_players_alive() == 1

    def run_game(self) -> int:
        """Start and run a game until completion, handling game logic as necessary."""
        self.add_to_history("start", json.loads(self._state.build_state_json(unmask=True)))
        while not self.game_is_over():
            self.broadcast_state()
            self.play_turn()
            self.next_turn()
        self.broadcast_state()
        winner = self._state.get_alive_players()[0]
        self.shout("Game is over!\n\nPlayer {} wins!".format(winner))
        self.shout("", "game_over")
        self.add_to_history("winner", {"winner": winner})
        return winner

    def play_turn(self) -> None:
        """Play one turn of the game."""
        current_player = self._state.get_current_player_id()
        action = self.query_player_action(current_player)
        self.add_to_history("action", action.history_rep())
        target = action.target

        def handle_block(chosen_reaction):
            # Handle block reactions
            self.add_to_history("block", chosen_reaction.history_rep())
            blocker = chosen_reaction.from_player
            query_challenge_players = [p for p in self._state.get_alive_players() 
                                       if p != blocker]
            challenges = self.query_challenges(query_challenge_players)
            if len(challenges) > 0:
                # Someone challenged the block, so resolve the challenge 
                chosen_challenge = self.choose_among_reactions(challenges)
                self.add_to_history("challenge", chosen_challenge.history_rep())
                challenger = chosen_challenge.from_player
                claimed_character = chosen_reaction.as_character
                losing_player = self._state.get_challenge_loser(claimed_character, 
                                                                blocker, challenger)
                card = self.query_player_card(losing_player)
                self._state.kill_player_card(losing_player, card)
                self.add_to_history("challenge_resolution", {"success": losing_player == blocker})
                self.add_to_history("block_resolution", {"success": losing_player != blocker})
                if losing_player == blocker:
                    self.execute_action(action, current_player, target, 
                                        ignore_if_dead=True)
                else:
                    self.exchange_player_card(blocker, chosen_reaction)
                    if self._config.pay_on_successful_challenges:
                        # Enforce any costs to original action executor
                        self.execute_action(action, current_player, only_pay_cost=True)
                self.shout("Player {} loses the challenge".format(losing_player))
            else:
                # Nobody challenged, so the block is successful
                self.add_to_history("block_resolution", {"success": True})
                # Enforce any costs to original action executor
                self.execute_action(action, current_player, only_pay_cost=True)
                self.shout("Action blocked with {}".format(chosen_reaction.as_character))    
        
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
                    handle_block(chosen_reaction)
                elif reaction_type == "challenge":
                    challenger = chosen_reaction.from_player
                    self.add_to_history("challenge", chosen_reaction.history_rep())
                    claimed_character = action.as_character
                    losing_player = self._state.get_challenge_loser(claimed_character, 
                                                                    current_player, challenger)
                    card = self.query_player_card(losing_player)
                    self._state.kill_player_card(losing_player, card)
                    self.shout("Player {} loses the challenge".format(losing_player))
                    self.add_to_history("challenge resolution", {"success": losing_player != challenger})
                    if losing_player == challenger:
                        self.exchange_player_card(current_player, action)
                        self.broadcast_state()
                        # Handle original action as usual, once the challenge has been settled
                        if action.is_blockable():
                            # Since any action that can be blocked and challenged can only be blocked 
                            # by the target, we only ask the target if they want to block
                            if target is None:
                                raise Exception(("Tried to query for a block for an Action after an "
                                                "unsuccessful challenge that doesn't have a target "
                                                "(only Steal and Assassinate can be blocked after "
                                                "an unsuccessful challenge.)"))
                            if self._state.player_is_alive(target):
                                block = self.query_player_block(target, action)
                                if block:
                                    handle_block(block)
                                else:
                                    self.execute_action(action, current_player, target)   
                            else:
                                self.execute_action(action, current_player, target, ignore_if_dead=True)   
                        else:
                            self.execute_action(action, current_player, target)   
                    else:
                        if self._config.pay_on_successful_challenges:
                            # Enforce any costs to original action executor
                            self.execute_action(action, current_player, only_pay_cost=True)
                else:           
                    raise ValueError("Invalid reaction type encountered")
            else:
                # Nobody reacted, so the action goes through
                self.execute_action(action, current_player, target)   

    def next_turn(self) -> None:
        """Move on to the next turn, updating the game state as necessary."""
        self._state.update_current_player() 
        # self.shout("It is now Player {}'s turn".format(self._state.get_current_player_id()))

    def choose_among_reactions(self, reactions : List[Reaction]) -> Reaction:
        """Given a list of reactions, return one based on the selection setting."""
        chosen_reaction = None
        mode = self._config.reaction_choice_mode
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
        self.shout("Player {} does a {}{}".format(player, reaction_type, " as {}".format(character) if is_block else ""))
        return chosen_reaction

    def execute_action(self, action: Action = None, source : int = None, target : int = None, 
                       ignore_if_dead : bool = False, only_pay_cost : bool = False) -> None:
        """Given an action, execute it based on the parameters provided."""

        # Add the action resolution to the history
        self.add_to_history("action_resolution", {"success": not only_pay_cost})

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

    def determine_action_message(self, player_id : int) -> str:
        query_msg = ("Player {}, what is your action?\n"
                     "You can: [I]ncome  [F]oreign Aid  [T]ax  [S]teal  [E]xchange"
                     .format(player_id))
        if self._state.player_can_assassinate(player_id):
            query_msg += "  [A]ssassinate"
        if self._state.player_can_coup(player_id):
            query_msg += "  [C]oup"
        return query_msg

    def query_player_action(self, player_id : int) -> Action:
        """Given a player, query them for an action, validating it and reprompting as necessary."""
        # First, check if the player has 10 coins and is forced to coup
        if self._state.player_must_coup(player_id):
            return self.query_player_coup_target(player_id)
        else:
            query_msg = self.determine_action_message(player_id)
            if self.is_ai_player(player_id):
                self.whisper(player=player_id, ai_query_type="action", ai_options=self._state.build_action_space(player_id))
            if not self.local:
                self.whisper(query_msg + "\n", player_id, "prompt")
            while True:
                response = input(query_msg + "\n") if self.local else self.get_response(player_id)
                try: 
                    action = self.translate_action_choice(response, source_id=player_id)
                except ValueError:
                    self.whisper("ERROR: invalid action name, please try again", player_id, "error")
                else:
                    valid = self.validate_action(action, player_id)
                    if valid:
                        as_character = " as " + action.as_character if action.as_character else ""
                        self.shout("Player {} {}".format(player_id, action.output_rep()) + as_character)
                        return action
                    self.whisper("Impossible action, please try again.", player_id, "error")

    def determine_reaction_message(self, target : int, player_id : int, action : Action) -> str:
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
        return "Player {}, are you going to {}?\n".format(player_id, message_action)

    def determine_reaction_space(self, target : int, player_id : int, action : Action) -> str:
        reaction_space = {}
        if target is not None:
            if target == player_id:
                reaction_space["Block"] = action.blockable_by
                reaction_space["Challenge"] = True
            else:
                reaction_space["Challenge"] = True
                reaction_space["Block"] = []
        else:
            challengeable = action.as_character 
            blockable = action.is_blockable()
            if challengeable and blockable:
                reaction_space["Block"] = action.blockable_by
                reaction_space["Challenge"] = True
            elif challengeable:
                reaction_space["Challenge"] = True
                reaction_space["Block"] = []
            elif blockable:
                reaction_space["Block"] = action.blockable_by
                reaction_space["Challenge"] = False
            else:
                 raise ValueError("Should not ask for reaction to unreactionable action")
        reaction_space["Pass"] = True
        return reaction_space

    def query_player_reactions(self, players : List[int], action : Action) -> List[Reaction]:
        """Given an action and a list of players to query, prompt players for reactions."""
        if self.local:
            reactions = []
            target = action.target
            for player_id in players:
                while True:
                    message = self.determine_reaction_message(target, player_id, action)
                    response = input(message)
                    try: 
                        reaction = self.translate_reaction_choice(response, player_id, action)
                    except ValueError:
                        self.whisper("Invalid reaction, please try again.", player_id)
                    else:
                        if reaction is None:
                            break
                        valid = self.validate_reaction(reaction, action)
                        if valid:
                            reactions.append(reaction)
                            break
                        self.whisper("Impossible reaction, please try again.", player_id)
            return reactions
        else:
            return self.ask_player_reactions(players, action)

    def ask_player_reactions(self, players : List[int], action : Action) -> List[Reaction]:
        """Query the server for reaction responses from a list of players."""
        target = action.target
        for i, player_id in enumerate(players):
            message = self.determine_reaction_message(target, player_id, action)
            if self.is_ai_player(player_id):
                self.whisper(player=player_id, ai_query_type="reaction", 
                             ai_options=self.determine_reaction_space(target, player_id, action))
            else:
                self.whisper(message, player_id, "prompt")
        reactions = [False for _ in players]
        print_wait_msg = True
        while False in reactions:
            for i, player_id in enumerate(players):
                if not reactions[i] and reactions[i] is not None:
                    response = self.get_response(player_id, sleep=False, print_wait=print_wait_msg)
                    if response is None:
                        continue
                    try: 
                        reaction = self.translate_reaction_choice(response, player_id, action)
                    except ValueError:
                        self.whisper("Invalid response, please try again.", player_id, "error")
                    else:
                        if reaction is None:
                            reactions[i] = None
                            continue
                        valid = self.validate_reaction(reaction, action)
                        if valid:
                            reactions[i] = reaction
                            continue
                        self.whisper("Impossible reaction, please try again.", player_id, "error")
            # Sleep in order to not poll too often, but only after we check each player's response
            if False in reactions:
                time.sleep(self.sleep_duration) 
                print_wait_msg = False
        return [r for r in reactions if r is not None]

    def query_player_block(self, player_id : int, action : Action) -> Reaction:
        """Query player for a block after an unsuccessful challenge."""
        query_msg = "Player {}, do you want to block?\n".format(player_id)
        if not self.local:
            if self.is_ai_player(player_id):
                self.whisper(player=player_id, ai_query_type="reaction", 
                             ai_options={"Challenge": False, "Block": action.blockable_by, "Pass": True})
            else:
                self.whisper(query_msg, player_id, "prompt")
        while True:
            response = input(query_msg) if self.local else self.get_response(player_id)
            try:
                reaction = self.translate_reaction_choice(response, player_id, action)
            except ValueError:
                self.whisper("Invalid block, please try again.", player_id)
            else:
                if reaction is None:
                    return None
                valid = self.validate_reaction(reaction, action, allow_challenges=False)
                if valid:
                    return reaction
                self.whisper("Invalid block, please try again.", player_id)
        
    def query_challenges(self, players : List[int]) -> List[Challenge]:
        """Given a list of players to query, ask them if they want to challenge."""
        if self.local:
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
                        self.whisper("Invalid response, please try again.", player_id)
            return challenges
        else:
            return self.ask_challenges(players)

    def ask_challenges(self, players : List[int]) -> List[Challenge]:
        """Query the server for challenge responses from a list of players."""
        for i, player_id in enumerate(players):
            query_msg = "Player {}, are you going to [C]hallenge?\n".format(player_id)
            if self.is_ai_player(player_id):
                self.whisper(player=player_id, ai_query_type="reaction", 
                             ai_options={"Challenge": True, "Block": [], "Pass": True})
            else:
                self.whisper(query_msg, player_id, "prompt")
        print_wait_msg = True
        challenges = [False for _ in players]        
        while False in challenges:
            for i, player_id in enumerate(players):
                if not challenges[i] and challenges[i] is not None:
                    response = self.get_response(player_id, sleep=False, print_wait=print_wait_msg)
                    if response is None:
                        continue
                    try: 
                        challenges[i] = self.translate_challenge_answer(response, player_id)
                    except ValueError:
                        self.whisper("Invalid response, please try again.", player_id, "error")
            # Sleep in order to not poll too often, but only after we check each player's response
            if False in challenges:
                time.sleep(self.sleep_duration)
                print_wait_msg = False
        return [c for c in challenges if c is not None]

    def query_player_coup_target(self, player_id : int) -> int:
        """Given a player who must coup, ask them who they are going to coup."""
        query_msg = "Player {}, who are you going to coup?\n".format(player_id)
        if not self.local:
            if self.is_ai_player(player_id):
                self.whisper(player=player_id, ai_query_type="action", ai_options=self._state.build_action_space(player_id))
            else:
                self.whisper(query_msg, player_id, "prompt")
        while True:
            response = input(query_msg) if self.local else self.get_response(player_id)
            try:
                action = self.translate_coup_target(response)
            except ValueError:
                self.whisper("Invalid coup target, please try again.", player_id, "error")
            else:
                valid = self.validate_action(action, player_id)
                if valid:
                    return action
                self.whisper("Invalid coup target, please try again.", player_id, "error")

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
            query_msg = "Player {}, one of your characters must die. Which one do you pick?\n".format(player_id)
            if not self.local:
                if self.is_ai_player(player_id):
                    self.whisper(player=player_id, ai_query_type="card_selection", ai_options=options)
                else:
                    self.whisper(query_msg, player_id, "prompt")
            while True:
                response = input(query_msg) if self.local else self.get_response(player_id)
                try:
                    card = self.translate_card_choice(response, options)
                    return card
                except ValueError:
                    self.whisper("ERROR: invalid card number, please try again.", player_id, "error")

    def translate_action_choice(self, response : str, source_id : int) -> Action:
        """Given an action response, translate it appropriately."""
        response = response.strip().lower()
        if response == "foreign aid":
            action_name = response
            target = None
        else:
            args = response.split(" ")
            action_name = args[0] if response != "foreign aid" else response
            target = None if len(args) == 1 else int(args[1])
        if action_name in [Steal.aliases, Assassinate.aliases, Coup.aliases]:
            if target is None:
                raise ValueError("Need to specify target for assassinate/steal")
     
        if action_name in Income.aliases:
            action = Income()
        elif action_name in ForeignAid.aliases:
            action = ForeignAid()
        elif action_name in Tax.aliases:
            action = Tax()
        elif action_name in Exchange.aliases:
            action = Exchange()
        elif action_name in Steal.aliases:
            action = Steal(target=target)
        elif action_name in Assassinate.aliases:
            action = Assassinate(target=target)
        elif action_name in Coup.aliases:
            action = Coup(target=target)
        else:
            raise ValueError("Invalid action name: {}".format(action_name))

        action.set_source(source_id)
        return action

    def translate_reaction_choice(self, response : str, source_id : int, 
                                  action : Action) -> Reaction:
        """Given a reaction response, translate it appropriately."""
        response = response.strip().lower()
        if len(response) == 0 or response == 'n':
            return None
        else:
            args = response.split(" ")
            reaction_type = args[0]
            if reaction_type in Block.aliases:
                character_options = action.blockable_by
                if character_options is None:
                    # action is not blockable, invalid response
                    raise ValueError("Cannot block unblockable action")
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
            elif reaction_type in Challenge.aliases:
                return Challenge(source_id)
            else:
                raise ValueError("Invalid reaction type")

    def translate_challenge_answer(self, response : str, source_id : int) -> Challenge:
        """Given a challenge response, translate it appropriately."""
        response = response.strip().lower()
        if len(response) == 0 or response in ["no", "n"]:  
            return None
        elif response in ["yes", "y"] or response in Challenge.aliases:
            return Challenge(source_id)
        else:
            raise ValueError("Invalid challenge answer")

    def translate_coup_target(self, response : str) -> Action:
        """Given a coup target response, translate it appropriately."""
        response = response.strip().lower()
        if response.startswith("coup "):
            response = response[5:]
        elif response.startswith("c "):
            response = response[2:]
        target = int(response)
        return Coup(target=target)

    def translate_card_choice(self, response : str, options : List[int]) -> int:
        response = response.strip()
        """Given a card choice to discard, translate it appropriately."""
        chosen_card = int(response)
        if chosen_card not in options:
            raise ValueError("Invalid card option") 
        return chosen_card       

    def validate_action(self, action : Action, player_id : int) -> bool:
        """Given an action, return whether it can be done given the current state."""
        return self._state.validate_action(action, player_id) 

    def validate_reaction(self, reaction : Reaction, action : Action, allow_challenges : bool = True) -> bool:
        """Given a reaction, return whether it can be done given the turn state."""
        reaction_type = reaction.reaction_type
        reactor = reaction.from_player
        if reaction_type == "block":
            target = action.target
            if target is not None:
                if target != reactor:
                    self.whisper("Cannot block action when not the target", reactor, "error")
                    return False
            if not action.is_blockable():
                self.whisper("Action is unblockable", reactor, "error")
                return False
            character = reaction.as_character
            blockable_by = action.blockable_by
            if character not in blockable_by:
                self.whisper("Specified character cannot block this action", reactor, "error")
                return False
            return True
        elif reaction_type == "challenge":
            if not action.is_challengeable() or not allow_challenges:
                self.whisper("Action cannot be challenged", reactor, "error")
                return False
            return True
        else:
            return False

    def exchange_player_card(self, player : int, move : Reaction) -> None:
        """Given a player and an action or reaction they did, exchange one of their cards appropriately. This is called when a player wins a challenge and needs to replace the challenged character."""
        character = move.as_character
        self._state.exchange_player_card(player, character)

    def get_config_status(self) -> str:
        return self._config_status
    
    def get_config_err_msg(self) -> str:
        return self._config_err_msg

    def shout(self, msg : str, shout_type : str = None) -> None:
        """Send a message to all players."""
        if self.local:
            print(msg)
        else:       
            self.shout_f(msg, shout_type)
            pass
    
    def whisper(self, msg : str = None, player : int = None, whisper_type : str = None, 
                ai_query_type : str = None, ai_options : dict = None, ai_info : dict = None) -> None:
        """Send a message only to a specific player."""
        if player is None:
            raise ValueError("Must specify a player to whisper to")
        if self.is_ai_player(player):
            if whisper_type is None:
                if (ai_query_type is None or ai_options is None) and ai_info is None:
                    assert False
                if ai_info:
                    self.whisper_f(json.dumps(ai_info), player, "ai_info")
                else:
                    self.whisper_f(json.dumps({"type": ai_query_type, "options": ai_options}), player, "ai_query")
            elif whisper_type == "error":
                raise Exception("Got invalid response from AI Agent")
        else:
            if msg is None:
                raise ValueError("Must specify a message for human players")
            if self.local:
                print(msg) 
            else:
                self.whisper_f(msg, player, whisper_type)

    def get_response(self, player : int, sleep : bool = True, print_wait : bool = True) -> str:
        """Query server for a response."""
        if print_wait:
            print("Waiting for a response from player {}...".format(player))
        while True:
            response = self.query_f(player)
            if response == "No response":
                if sleep:
                    time.sleep(self.sleep_duration)
                    continue
                else:
                    return None
            elif response is not None:
                return response
            else:
                assert False

    def broadcast_state(self) -> None:
        self._state.broadcast_state()
    
    def add_to_history(self, event_type : str, event_info : dict) -> None:
        # Add the action resolution to the history
        self._state.add_to_history(event_type, event_info)
        print(event_type, event_info)

    def is_ai_player(self, i : int) -> bool:
        return i in self.game_info.ai_players

if __name__ == "__main__":
    engine = Engine(parse_args())
    if not engine.get_config_status():
        print("\nInvalid configuration: " + engine.get_config_err_msg().split("'")[1])
        print("\nCannot run game; exiting.")
    else:
        winner = engine.run_game()
