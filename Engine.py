import random, time
from classes.Card import Card
from State import State
from classes.actions import Action, Income, ForeignAid, Tax, Steal, Assassinate, Coup
from classes.reactions import Reaction, Block, Challenge
from Config import Config

class Engine:

    def __init__(self) -> None:
        self.config = Config()
        self._state = State(self.config)
        self.run_game()

    def game_is_over(self) -> bool:
        return self._state.n_players_alive() == 1

    def run_game(self):
        while not self.game_is_over():
            print(self._state)
            current_player = self._state.get_current_player_id()
            action = self.query_player_action(current_player)
            target = action.get_property("target")
            
            if not action.is_blockable() and not action.is_challengeable():
                # Action always goes through, e.g. Income
                self.execute_action(action, current_player, target)
            else:
                # Blocks and/or Challenges are possible. See if anyone decides to challenge
                query_players = [target] if target is not None \
                    else [p for p in self._state.get_alive_players() if p != current_player]
                reactions = self.query_player_reactions(query_players, action)
                if len(reactions) > 0:
                    chosen_reaction = self.choose_among_reactions(reactions)
                    reaction_type = chosen_reaction.get_property("reaction_type")
                    if reaction_type == "block":
                        blocker = chosen_reaction.get_property("from_player")
                        query_challenge_players = [p for p in self._state.get_alive_players() if p != blocker]
                        challenges = self.query_challenges(query_challenge_players)
                        if len(challenges) > 0:
                            chosen_challenge = self.choose_among_reactions(challenges)
                            challenger = chosen_challenge.get_property("from_player")
                            claimed_character = chosen_reaction.get_property("as_character")
                            losing_player = self._state.get_challenge_loser(claimed_character, blocker, challenger)
                            card = self.query_player_card(losing_player)
                            self._state.kill_player_card(losing_player, card)
                            if losing_player == blocker:
                                self.execute_action(action, current_player, target, ignore_if_dead=True)
                            else:
                                # Enforce any costs to original action executor
                                self.execute_action(action, current_player, only_pay_cost=True)
                                self.exchange_player_card(blocker, chosen_reaction)
                            print("Player {} loses the challenge".format(losing_player))
                        else:
                            # Enforce any costs to original action executor
                            self.execute_action(action, current_player, only_pay_cost=True)
                            print("Action blocked with {}".format(chosen_reaction.get_property("as_character")))    
                    elif reaction_type == "challenge":
                        challenger = chosen_reaction.get_property("from_player")
                        claimed_character = action.get_property("as_character")
                        losing_player = self._state.get_challenge_loser(claimed_character, current_player, challenger)
                        card = self.query_player_card(losing_player)
                        self._state.kill_player_card(losing_player, card)
                        if losing_player == challenger:
                            self.execute_action(action, current_player, target, ignore_if_dead=True)
                            self.exchange_player_card(current_player, action)
                        else:
                            # Enforce any costs to the original player, the challenge loser
                            self.execute_action(action, current_player, only_pay_cost=True)
                        print("Player {} loses the challenge".format(losing_player))
                    else:           
                        raise ValueError("Invalid reaction type encountered")
                else:
                    self.execute_action(action, current_player, target)
            self.next_turn()
     
        print("Game is over! \n Winner is: Player {}".format(self._state.get_alive_players()[0]))
    
    def next_turn(self):
        self._state.update_current_player() 

    def choose_among_reactions(self, reactions):
        # First mode, random mode, first challenge, first block, random challenge first, random block first
        chosen_reaction = None
        mode = self.config.reaction_choice_mode
        if mode == "first":
            chosen_reaction = reactions[0]
        elif mode == "random":
            chosen_reaction = random.choice(reactions)
        elif mode == "first_challenge":
            for reaction in reactions:
                if reaction.get_property("reaction_type") == "challenge":
                    chosen_reaction = reaction
                    break
                chosen_reaction = reactions[0] 
        elif mode == "first_block":
            for reaction in reactions:
                if reaction.get_property("reaction_type") == "block":
                    chosen_reaction = reaction
                    break
                chosen_reaction = reactions[0] 
        elif mode == "random_challenge":
                desired = [r for r in reactions if r.get_property("reaction_type") == "challenge"]
                if len(desired) > 0:
                    chosen_reaction = random.choice(desired)
                else:
                    chosen_reaction = random.choice(reactions)
        elif mode == "random_block":
                desired = [r for r in reactions if r.get_property("reaction_type") == "block"]
                if len(desired) > 0:
                    chosen_reaction = random.choice(desired)
                else:
                    chosen_reaction = random.choice(reactions)
        player = chosen_reaction.get_property("from_player")
        reaction_type = chosen_reaction.get_property("reaction_type")
        is_block = reaction_type == "block"
        character = chosen_reaction.get_property("as_character") if is_block else None
        print("Player {} does a {}{}".format(player, reaction_type, " as {}".format(character) if is_block else ""))
        return chosen_reaction

    def execute_action(self, action: Action = None, source : int = None, target : int = None, ignore_if_dead : bool = False, only_pay_cost : bool = False):
        ignore_killing = False
        if not only_pay_cost:
            # Query affected player if necessary
            if not action.ready():
                card = self.query_player_card(target, ignore_if_dead)
                if card is not None:
                    action.set_property("kill_card_id", card)
                else:   
                    # card is None because the player is already dead and there is no card to choose
                    ignore_killing = True
        self._state.execute_action(source, action, ignore_killing, only_pay_cost)

    def query_player_action(self, player_id : int) -> Action:
        # First, check if the player has 10 coins and is forced to coup
        if self._state.player_must_coup(player_id):
            return self.query_player_coup_target(player_id)
        else:
            while True:
                response = input("Player {}, what is your action?\n".format(player_id))
                try: 
                    action = self.translate_action_choice(response)
                except ValueError:
                    print("Invalid action, please try again.")
                else:
                    valid = self.validate_action(action, player_id)
                    if valid:
                        return action
                    print("Impossible action, please try again.")
                    

    def query_player_reactions(self, players : list, action : Action) -> list:
        reactions = []
        for player_id in players:
            while True:
                response = input("Player {}, are you going to react?\n".format(player_id))
                try: 
                    reaction = self.translate_reaction_choice(response, player_id)
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

    def query_challenges(self, players : list) -> list:
        challenges = []
        for player_id in players:
            while True:
                response = input("Player {}, are you going to challenge?\n".format(player_id))
                try: 
                    reaction = self.translate_challenge_answer(response, player_id)
                    if reaction is not None:
                        challenges.append(reaction)
                    break
                except ValueError:
                    print("Invalid response, please try again.")
        return challenges

    def query_player_coup_target(self, player_id : int) -> int:
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
                response = input("Player {}, which card do you pick?\n".format(player_id))
                try:
                    card = self.translate_card_choice(response, options)
                    return card
                except ValueError:
                    print("Invalid card, please try again.")

    def translate_action_choice(self, response : str) -> Action:
        args = response.split(" ")
        action_name = args[0]
        target = None if len(args) == 1 else int(args[1])
     
        if action_name == "income":
            return Income.Income()
        elif action_name == "foreignaid":
            return ForeignAid.ForeignAid()
        elif action_name == "tax":
            return Tax.Tax()
        elif action_name == "steal":
            return Steal.Steal(target=target)
        elif action_name == "assassinate":
            return Assassinate.Assassinate(target=target)
        elif action_name == "coup":
            return Coup.Coup(target=target)
        else:
            print("ERROR: invalid action name: {}".format(action_name))
            raise ValueError("Invalid action name: {}".format(action_name))

    def translate_reaction_choice(self, response : str, source_id : int) -> Reaction:
        if len(response) == 0:
            return None
        else:
            args = response.split(" ")
            reaction_type = args[0]
            if reaction_type == "block":
                if len(args) != 2:
                    raise ValueError("Invalid number of arguments for block")
                character = args[1]
                return Block.Block(source_id, character)
            elif reaction_type == "challenge":
                return Challenge.Challenge(source_id)
            else:
                raise ValueError("Invalid reaction type")

    def translate_challenge_answer(self, response : str, source_id : int) -> Challenge:
        if len(response) == 0 or response == "no":  
            return None
        elif response == "yes":
            return Challenge.Challenge(source_id)
        else:
            raise ValueError("Invalid challenge answer")

    def translate_coup_target(self, response : str) -> Action:
        target = int(response)
        return Coup.Coup(target=target)

    def translate_card_choice(self, response : str, options : list) -> int:
        chosen_card = int(response)
        if chosen_card not in options:
            print("ERROR: invalid card number: {}".format(chosen_card))
            raise ValueError("Invalid card option") 
        return chosen_card       

    def validate_action(self, action : Action, player_id : int) -> bool:
        return self._state.validate_action(action, player_id) 

    def validate_reaction(self, reaction : Reaction, action : Action) -> bool:
        reaction_type = reaction.get_property("reaction_type")
        if reaction_type == "block":
            if not action.is_blockable():
                print("Cannot block action")
                return False
            character = reaction.get_property("as_character")
            blockable_by = action.get_property("blockable_by")
            if character not in blockable_by:
                print("Specified character cannot block this action")
                return False
            return True
        elif reaction_type == "challenge":
            if not action.is_challengeable():
                print("Cannot challenge action")
                return False
            return True
        else:
            return False

    def exchange_player_card(self, player : int, move) -> None:
        character = move.get_property("as_character")
        self._state.exchange_player_card(player, character)

if __name__ == "__main__":
    Engine()
