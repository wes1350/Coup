"""Basic agent using a neural network."""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random

if __name__ == "__main__":
    from utils.game import *
    from utils.responses import *
    from utils.network import *
    from Agent import Agent
else:
    from .utils.game import *
    from .utils.responses import *
    from .utils.network import *
    from .Agent import Agent


class CoupNN(nn.Module):
    
    def __init__(self, input_size, hidden_size, n_players):
        super(CoupNN, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size

        self.hidden_state = torch.randn(hidden_size).view(1, 1, -1)
        self.cell_state = torch.zeros(hidden_size).view(1, 1, -1)

        self.lstm = nn.LSTM(input_size, hidden_size)
        self.value_map = nn.Linear(hidden_size, n_players)

    def forward(self, input_vector):
        out, (self.hidden_state, self.cell_state) = self.lstm(input_vector, (self.hidden_state, self.cell_state))
        probs = self.value_map(out)
        # Return hidden and cell state so that we can update them when receiving an event
        return probs, self.hidden_state, self.cell_state

    def forward_no_update(self, input_vector, additional_input_vectors : list = []):
        hidden = self.hidden_state.clone().detach()
        cell = self.cell_state.clone().detach()
        out, (hidden, cell) = self.lstm(input_vector, (hidden, cell))
        for iv in additional_input_vectors:
            out, (hidden, cell) = self.lstm(iv, (hidden, cell))

        values = self.value_map(out)
        probs = nn.Softmax(dim=2)(values).view(-1).tolist()
        print("Forward no update results:", probs)
        return probs

class PytorchAgent(Agent):
    def __init__(self, input_size, hidden_size, n_players):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.n_players = n_players

        self.model = CoupNN(input_size, hidden_size, n_players)
        self.loss_function = nn.CrossEntropyLoss()
        self.optimizer = optim.SGD(self.model.parameters(), lr=0.1)

        self.id = None
        self.cards = None

    def convert_event_to_vector(self, e):
        # return torch.randn(input_size).view(1, 1, -1)
        #############
        rep = [0] * self.input_size

        event = e["event"]
        info = e["info"]

        chars = ["Ambassador", "Assassin", "Captain", "Contessa", "Duke"]
        
        if event == "action":
            rep[0] = 1
            action_idx = ["Income", "ForeignAid", "Tax", "Exchange", "Steal", "Assassinate", "Coup"].index(info["type"])
            rep[1 + action_idx] = 1
            if info["as_character"] is not None:
                claimed_idx = ["Ambassador", "Assassin", "Captain", "Duke"].index(info["as_character"]) 
                rep[8 + claimed_idx] = 1
            rep[18 + info["from_player"]] = 1
            if info["target"] is not None:
                rep[20 + info["target"]] = 1
        elif event == "action_resolution":
            rep[0] = 1
            rep[22] = 1
            if info["success"]:
                rep[23] = 1
        elif event == "block":
            rep[12] = 1
            if info["as_character"] is not None:
                claimed_idx = ["Ambassador", "Captain", "Contessa", "Duke"].index(info["as_character"])
                rep[13 + claimed_idx] = 1
            rep[18 + info["from"]] = 1
        elif event == "block_resolution":
            rep[12] = 1
            rep[22] = 1
            if info["success"]:
                rep[23] = 1
        elif event == "challenge":
            rep[17] = 1
            rep[18 + info["from"]] = 1
        elif event == "challenge_resolution":
            rep[17] = 1
            rep[22] = 1
            if info["success"]:
                rep[23] = 1
        elif event == "winner":
            rep[18 + info["winner"]] = 1
        elif event == "loser":
            rep[18 + info["loser"]] = 1
        elif event == "card_loss":
            rep[18 + info["player"]] = 1
            rep[29 + chars.index(info["character"])] = 1
        elif event == "draw":
            rep[29 + chars.index(info[0])] = 1
            rep[34 + chars.index(info[1])] = 1
        elif event == "card_swap":
            rep[18 + info["player"]] = 1
            if info["from"] is not None:
                rep[29 + chars.index(info["from"])] = 1
            if info["to"] is not None:
                rep[34 + chars.index(info["to"])] = 1
        elif event == "state":
            rep[39 + info["playerId"]] = 1
            # update_player_id(player_id, info["playerId"])
            self.id = info["playerId"]
            rep[41 + info["currentPlayer"]] = 1
            player_info = info["players"]
            n_cards = len(player_info[0]["cards"])
            for i, p in enumerate(player_info):
                rep[43 + i] = p["coins"]
            my_cards = [player_info[info["playerId"]]["cards"][i] for i in range(n_cards)]
            # update_hand(player_cards, my_cards)
            self.cards = my_cards
            my_chars = [chars.index(c["character"]) for c in my_cards]
            rep[45 + my_chars[0]] = 1
            rep[50 + my_chars[1]] = 1
            my_life_statuses = [c["alive"] for c in my_cards]
            rep[55] = 1 if my_life_statuses[0] else 0
            rep[56] = 1 if my_life_statuses[1] else 0
            
            opponent_idx = -1  # Order opponents from 0 to n-2 
            for i in range(self.n_players):  
                if i != info["playerId"]:
                    opponent_idx += 1
                    opponent_cards = [player_info[info["playerId"]]["cards"][i] for i in range(n_cards)]
                    opp_chars = [c["character"] for c in opponent_cards]
                    if opp_chars[0] is not None:
     #                    rep[57 + opponent_idx * 10 + chars.index(opp_chars[0])] = 1
                         rep[57 + chars.index(opp_chars[0])] = 1
                    
                    if opp_chars[1] is not None:
    #                     rep[62 + opponent_idx * 10 + chars.index(opp_chars[1])] = 1
                         rep[62 + chars.index(opp_chars[1])] = 1
        return torch.FloatTensor(rep).view(1, 1, -1)

    def convert_option_to_events(self, option, option_type):
        """Converts an option list into the corresponding event(s).
           For actions and reactions, options are length-2 tuples.
           For card selection, options are numbers.
           For exchanges, options are either numbers or length-2 tuples."""
        if option_type == "action":
            name = option[0] if isinstance(option, tuple) else option
            if name == "tax":
                claimed = "Duke"
            elif name == "steal":
                claimed = "Captain"
            elif name == "exchange":
                claimed = "Ambassador"
            elif name == "assassinate":
                claimed = "Assassin"
            else:
                claimed = None
            return [{"event": "action", "info": {"type": name, "as_character": claimed, "from_player": self.id, 
                                                 "target": None if isinstance(option, str) else option[1]}}]
        elif option_type == "reaction":
            return [{"event": "reaction", "info": {"type": option[0], "from": self.id, "as_character": option[1]}}]
        elif option_type == "card_selection":
            return [{"event": "card_loss", "info": {"character": self.cards[option]["character"], "player": self.id}}]
        elif option_type == "exchange":
            events = []
            alive_cards = [c for c in self.cards if c["alive"]]
            for i in range(len(alive_cards)):
                events.append({"event": "card_swap", 
                               "info": {"from": alive_cards[i]["character"], 
                                        "to": option[i], "player": self.id}})
            return events

    def convert_option_to_vectors(self, option, option_type):
        return [self.convert_event_to_vector(e) for e in self.convert_option_to_events(option, option_type)]

    def update(self, event):
        _, self.hidden_state, self.cell_state = self.model(self.convert_event_to_vector(event))

    def decide_action(self, options):
        #ask neural net for best action
    #     possible_actions = possible_responses(options)
    #     action = random.choice(possible_actions)
    #     if isinstance(options[action], list):
    #         target = random.choice(options[action])
    #         return convert(action, target)
    #     return convert(action)

        ###########
        option_list = extract_options(options, "action")
        win_probs = []
        for option in option_list:
            vectors = self.convert_option_to_vectors(option, "action")
            win_p = self.model.forward_no_update(vectors[0], vectors[1:])
            my_win_p = win_p[self.id]
            win_probs.append(my_win_p)
        best_option = option_list[win_probs.index(max(win_probs))]
        return convert(*best_option)

    def decide_reaction(self, options):
    #     ask neural net for best reaction
    #     return decline()
        ###########
    #     option_list = extract_options(options)
    #     win_probs = [model.forward_no_update(convert_option_to_vector(option, "reaction"))[player_id] for option in option_list]
    #     best_option = win_probs[win_probs.index(max(win_probs))]
    #     return convert(*best_option)
        option_list = extract_options(options, "reaction")
        win_probs = []
        for option in option_list:
            vectors = self.convert_option_to_vectors(option, "reaction")
            win_p = self.model.forward_no_update(vectors[0], vectors[1:])
            my_win_p = win_p[self.id]
            win_probs.append(my_win_p)
        best_option = option_list[win_probs.index(max(win_probs))]
        return convert(*best_option)

        
    def decide_card(self, options):
     #    ask neural net for best card to choose
        option_list = extract_options(options, "card_selection")
        win_probs = []
        for option in option_list:
            vectors = self.convert_option_to_vectors(option, "card_selection")
            win_p = self.model.forward_no_update(vectors[0], vectors[1:])
            my_win_p = win_p[self.id]
            win_probs.append(my_win_p)
        return option_list[win_probs.index(max(win_probs))]


    def decide_exchange(self, options):
      #   ask neural net for best exchange choices
        option_list = extract_options(options, "exchange")
        win_probs = []
        for option in option_list:
            if isinstance(option, list):
                exchange_characters = [t[1] for t in option]
            else:
                exchange_characters = [option[1]]
            vectors = self.convert_option_to_vectors(exchange_characters, "exchange")
            win_p = self.model.forward_no_update(vectors[0], vectors[1:])
            my_win_p = win_p[self.id]
            win_probs.append(my_win_p)
        best_option = option_list[win_probs.index(max(win_probs))]
        if isinstance(best_option, list):
            return choose_exchange_cards([o[0] for o in best_option])
        else:
            return choose_exchange_cards([best_option[0]])


if __name__ == "__main__":
    start(PytorchAgent(input_size=67, hidden_size=10, n_players=2))
