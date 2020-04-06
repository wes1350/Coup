import random, time
from classes.Card import Card
from State import State
from classes.actions import Action, Income, ForeignAid, Tax, Steal, Assassinate, Coup
from classes.reactions import Reaction, Block, Challenge

class Engine:

    def __init__(self) -> None:
        self._state = State(n_players=3)
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
                    chosen_reaction = reactions[0]
                    reaction_type = chosen_reaction.get_property("reaction_type")
                    if reaction_type == "block":
                        blocker = chosen_reaction.get_property("from_player")
                        query_challenge_players = [p for p in self._state.get_alive_players() if p != blocker]
                        challenges = self.query_challenges(query_challenge_players)
                        if len(challenges) > 0:
                            chosen_challenge = challenges[0]
                            challenger = chosen_challenge.get_property("from_player")
                            claimed_character = chosen_reaction.get_property("as_character")
                            losing_player = self._state.get_challenge_loser(claimed_character, blocker, challenger)
                            card = self.query_player_card(losing_player)
                            self._state.kill_player_card(losing_player, card)
                            if losing_player == blocker:
                                self.execute_action(action, current_player, target)
                            print("Player {} loses the challenge".format(losing_player))
                        else:
                            print("Action blocked with {}".format(chosen_reaction.get_property("as_character")))    
                    elif reaction_type == "challenge":
                        challenger = chosen_reaction.get_property("from_player")
                        claimed_character = action.get_property("actor")
                        losing_player = self._state.get_challenge_loser(claimed_character, current_player, challenger)
                        card = self.query_player_card(losing_player)
                        self._state.kill_player_card(losing_player, card)
                        if losing_player == challenger:
                            self.execute_action(action, current_player, target)
                        print("Player {} loses the challenge".format(losing_player))
                    else:           
                        raise ValueError("Invalid reaction type encountered")
                else:
                    self.execute_action(action, current_player, target)
            self.next_turn()
     
        print("Game is over! \n Winner is: Player {}".format(self._state.get_alive_players()[0]))
    
    def next_turn(self):
        self._state.update_current_player() 

    def execute_action(self, action: Action, source : int, target : int):
        # Query affected player if necessary
        if not action.ready():
            card = self.query_player_card(target)
            action.set_property("kill_card_id", card)
        self._state.execute_action(source, action)

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
            

    def query_player_card(self, player_id : int) -> int:
        # First, determine whether we need to query the player for a card
        options = self._state.get_player_living_card_ids(player_id)
        if len(options) == 0:
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

if __name__ == "__main__":
    Engine()
