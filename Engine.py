import random, time
from classes.Card import Card
from State import State
from classes.actions import Action, Income, ForeignAid, Tax, Steal, Assassinate, Coup
from classes.reactions import Reaction, Block, Challenge

class Engine:

    def __init__(self) -> None:
        self._state = State(n_players=3)
        self.run_game()

    def run_game(self):
        while not self.game_is_over():
            print(self._state)
            current_player = self._state.get_current_player_id()

            # query current player for action
            action = self.query_player_action(current_player)
            target = action.get_property("target")
            
            if not action.is_blockable() and not action.is_challengeable():
                # No counter actions possible

                # query affected player if necessary
                if not action.ready():
                    card = self.query_player_card(target)
                    action.set_property("kill_card_id", card)

                # handle action 
                self._state.execute_action(current_player, action)
                self._state.update_current_player() 
 
            else:
                # Reactions possible

                # Decide who to query
                query_players = [target] if target is not None else [p for p in self._state.get_alive_players() if p != current_player]
                reactions = self.query_player_reactions(query_players, action)
                if len(reactions) > 0:
                    chosen_reaction = reactions[0]
                    reaction_type = chosen_reaction.get_property("reaction_type")
                    if reaction_type == "block":
                        pass
                    elif reaction_type == "challenge":
                        # Settle the challenge
                        challenger = chosen_reaction.get_property("from_player")
                        claimed_character = action.get_property("actor")
                        # Decide who loses and remove one of their cards
                        losing_player = self._state.get_challenge_loser(claimed_character, current_player, challenger)
                        card = self.query_player_card(losing_player)
                        self._state.kill_player_card(losing_player, card)
                        # If the challenger lost, execute the original action
                        if losing_player == challenger:
                            self._state.execute_action(current_player, action)
                    else:           
                        raise ValueError("Invalid reaction type encountered")
                    # Finally move on to the next player
                    self._state.update_current_player() 
                else:
                    # handle action 
                    self._state.execute_action(current_player, action)
                    self._state.update_current_player() 
                
     
        print("Game is over! \n Winner is: Player {}".format(self._state.get_alive_players()[0]))

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
                    

    def query_player_reactions(self, players : list, action : Action):
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
            

    def query_player_card(self, player_id : int):
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

    def game_is_over(self):
        return self._state.n_players_alive() == 1

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
