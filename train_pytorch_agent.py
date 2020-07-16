from Engine import Engine
from agents.PytorchAgent import PytorchAgent
import torch.optim as optim

a = PytorchAgent(input_size=67, hidden_size=10, n_players=2)
b = PytorchAgent(input_size=67, hidden_size=10, n_players=2)

local_ais = {0: a, 1: b}
# print(a.model.hidden_state)
# print(b.model.hidden_state)
# for n, p in a.model.named_parameters():   
#     print(n, p.data)

print("Starting Training")
training_winners = []
for i in range(1000):
    if i % 100 == 0:
        print("Training Iteration " + str(i + 1))
        print("Win percentage this epoch:", len([r for r in training_winners[i-100:i] if r == 0]))
        print([x for x in a.model.named_parameters()][-1])
    e = Engine(local_ais=local_ais)
    winner = e.run_game()
    training_winners.append(winner)

#     print(a.model.hidden_state)
#     print(b.model.hidden_state)
#     time.sleep(2)
#     for name, p in a.model.named_parameters():   
#         print(name) 
#         print(p.data)
#         time.sleep(2)
#         break

    a.train_model(winner)
    a.events = []
#     for name, p in a.model.named_parameters():   
#         print(name) 
#         print(p.data)
#         time.sleep(2)
#         break

print("Player A win percentage for training:", 0.001 * len([r for r in training_winners if r == 0]))


testing_winners = []

print("Starting Testing")
testing_winners = []
for i in range(100):
    if i % 10 == 0:
        print("Testing Iteration " + str(i + 1))
    e = Engine(local_ais=local_ais)
    winner = e.run_game()
    testing_winners.append(winner)


print("Player A win percentage for testing:", 0.01 * len([r for r in testing_winners if r == 0]))
