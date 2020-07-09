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
else:
    from .utils.game import *
    from .utils.responses import *
    from .utils.network import *

input_size = 10
hidden_size = 10
n_players = 2

hidden_state = torch.randn(1, hidden_size).view(1, 1, -1)
cell_state = torch.randn(1, hidden_size).view(1, 1, -1)


class NeuralAgent(nn.Module):
    
    def __init__(self, input_size, hidden_size, n_players):
        super(NeuralAgent, self).__init__()
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size)
        self.value_map = nn.Linear(hidden_size, n_players)

    def forward(self, input_vector):
        # Might need to use view on layer inputs
        out, (hidden, cell) = self.lstm(input_vector)
        probs = self.value_map(hidden)
        print(nn.Softmax(dim=2)(probs), flush=True)
        print(out)
        print(hidden, flush=True)
        print(cell, flush=True)
        print("---"*20, flush=True)
        return probs, hidden, cell

    def forward_no_update(self, input_vector):
        _, (hidden, _) = self.lstm(input_vector)
        values = self.value_map(hidden)
        return nn.Softmax(dim=2)(values)

model = NeuralAgent(input_size, hidden_size, 2)
loss_function = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.1)

def convert_event_to_vector(event):
    return torch.randn(input_size).view(1, 1, -1)

def convert_option_to_event(option):
    pass

def convert_option_to_vector(option):
    return convert_event_to_vector(convert_option_to_event(option))

def extract_options(options):
    pass

def extract_win_prob(probs, player_id):
    pass

def update(hidden, cell):
    def update_NN_params(event):
        _, hidden, cell = model(convert_event_to_vector(event))
    return update_NN_params

def decide_action(options):
    #ask neural net for best action
    possible_actions = possible_responses(options)
    action = random.choice(possible_actions)
    if isinstance(options[action], list):
        target = random.choice(options[action])
        return convert(action, target)
    return convert(action)

def decide_reaction(options):
#     ask neural net for best reaction
    return decline()
    ###########
    option_list = extract_options(options)
    win_probs = [extract_win_prob(model.forward_no_update(convert_option_to_vector(option))) for option in option_list]
    best_option = win_probs.index(max(win_probs))
    return convert(best_option)
    
def decide_card(options):
 #    ask neural net for best card to choose
    return random.choice(options)

def decide_exchange(options):
  #   ask neural net for best exchange choices
    return choose_exchange_cards(random.sample(options["cards"].keys(), options["n"]))


if __name__ == "__main__":
    start(on_action=decide_action, on_reaction=decide_reaction, 
          on_card=decide_card, on_exchange=decide_exchange, update_f=update(hidden_state, cell_state))
