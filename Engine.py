import random, time
from classes.Card import Card
from State import State
from classes.actions import Action, Income, ForeignAid, Tax, Steal, Assassinate, Coup

class Engine:

    def __init__(self) -> None:
        self._state = State(n_players=3)
        self.run_game()

    def run_game(self):
        while not self.game_is_over():
            print(self._state)
            current_player = self._state.get_current_player_id()

            # query current player for action
            translated_response = self.query_player(current_player, "action") 
            
            if True:
                # No counter actions possible

                # query affected player if necessary
                if translated_response["needs_card_chosen"]:
                    card_response = self.query_player(translated_response["target"], "choose_card")
                    translated_card = card_response["chosen_card"]
                    action = self.construct_action(translated_response, translated_card)
                else:
                    action = self.construct_action(translated_response)

                # handle action 
                self._state.execute_action(current_player, action)
                self._state.update_current_player() 
 
            else:
                # Reactions possible
                pass
     
        print("Game is over! \n Winner is: Player {}".format(self._state.get_alive_players()[0]))

    def query_player(self, player_id : int, query_type : str) -> dict:
        while True:
            if query_type == "action":
                response = input("Player {}, what is your action?\n".format(player_id))
            elif query_type == "choose_card":
                response = input("Player {}, which card do you pick?\n".format(player_id))
            else:
                raise ValueError("Invalid query type")
            try: 
                translation = self.translate_response(response, query_type)
                break
            except ValueError:
                print("Invalid input, please try again.")
        return translation

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

    def translate_response(self, response : str, query_type : str) -> dict:
        if query_type == "action": 
            translation = {"needs_card_chosen": False}
            args = response.split(" ")
            translation["action_name"] = args[0]
            if args[0] in ["income", "foreignaid", "tax"]:
                pass
            elif args[0] == "steal":
                if len(args) != 2:
                    raise ValueError("Steal takes two arguments")
                translation["target"] = int(args[1])
            elif args[0] == "assassinate":
                if len(args) != 2:
                    raise ValueError("Assassinate takes two arguments")
                translation["target"] = int(args[1])
                translation["needs_card_chosen"] = True    
            elif args[0] == "coup":
                translation["target"] = int(args[1])
                translation["needs_card_chosen"] = True    
            else:
                raise ValueError("Invalid action name")
        elif query_type == "choose_card":
            translation = {}
            chosen_card = int(response)
            if chosen_card not in [0, 1]:
                raise ValueError("Invalid card option") 
            translation["chosen_card"] = chosen_card

        return translation       

    def construct_action(self, response : dict, card : int = None) -> Action:
        action_name = response["action_name"]
        if action_name == "income":
            return Income.Income()
        elif action_name == "foreignaid":
            return ForeignAid.ForeignAid()
        elif action_name == "tax":
            return Tax.Tax()
        elif action_name == "steal":
            return Steal.Steal(target=response["target"])
        elif action_name == "assassinate":
            return Assassinate.Assassinate(target=response["target"], card_id=card)
        elif action_name == "coup":
            return Coup.Coup(target=response["target"], card_id=card)

if __name__ == "__main__":
    Engine()
