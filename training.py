import shutil
from Engine import Engine
from agents import *


main_agent = './KerasModel/training'
hold_agent = './KerasModel/training/hold'
untrained_agent = './KerasModel/untrained'

checkpoint = './KerasModel/checkpoint'

def update_hold(hold_location, source_location):
    # updates the hold model with the latest model
    print('deleting hold model')
    shutil.rmtree(hold_location, ignore_errors=True)
    print('updating hold model with current model')
    shutil.copytree(source_location, hold_location)


def self_train(training_location, hold_location):
    n = 10000
    wins = 0
    for i in range(n):
        print("TRAINING EPISODE: ", i)
        if (i % 1000 == 0):
            update_hold(hold_location, training_location)

        engine = Engine(local_ais = {0: KerasAgent(model_location=training_location, training=True, debug=False), 
                            1: KerasAgent(model_location=hold_location, training=False, debug=False)})
        winner =  engine.run_game()
        wins += 1 if winner == 0 else 0
        print("WIN RATE: ", wins/(i + 1))
    return wins/n
    
def evaluate_with_model(training_location, eval_model_location, n):
    wins = 0
    for i in range(n):
        engine = Engine(local_ais = {0: KerasAgent(model_location=training_location, training=False, debug=False), 
                            1: KerasAgent(model_location=eval_model_location, training=False, debug=False)})
        winner = engine.run_game()
        wins += 1 if winner == 0 else 0
        print("WIN RATE: ", wins/(i + 1))
    return wins/n

def benchmark(model_location, n=100):
    stats = {}
    # bench marking agaisnt other Agents
    agents = [TaxAgent()]
    for agent in agents: 
        wins = 0
        agent_name = type(agent).__name__
        print(f"Benchmarking against {agent_name}...")
        for i in range(n):
            engine = Engine(local_ais = 
            {0: KerasAgent(model_location=model_location, training=False),
             1: agent})
            winner = engine.run_game()
            wins += 1 if winner == 0 else 0
            win_rate = wins / (i + 1)
        print("Win rate: ", win_rate)
        stats[agent_name] = win_rate
    print(stats)
    return stats

benchmark(checkpoint)


# implement mini batch updating