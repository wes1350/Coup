from datetime import datetime
import pickle
import numpy as np
import shutil
from Engine import Engine
from keras import models, layers
from tensorflow import keras
from agents import *

class Gym():
    def __init__(self, epoch=10, gamma=0.9, epsilon=.1):
        self.training_location = "./KerasModel/training"
        self.holding_location = "./KerasModel/training/hold"
        self.untrained_location = "./KerasModel/untrained"
        self.checkpoints_location = "./KerasModel/checkpoints"

        # directory where all logs will be saved
        self.log_location = "./Logs/KerasModel"

        # hyperparameters
        self.gamma = 0.99
        self.epoch = epoch
        self.epsilon = epsilon

    def update_hold(self, hold_location, source_location):
        # updates the hold model with the latest model
        print('deleting hold model')
        shutil.rmtree(hold_location, ignore_errors=True)
        print('updating hold model with current model')
        shutil.copytree(source_location, hold_location)

    def load_model(self, model_location):
        model = None
        try:
            print("Loading model from ", model_location)
            model = keras.models.load_model(model_location)
            print("Loaded model")
        except Exception as e:
            print("Unable to load model")
            raise(e)
        return model

    def discount_rewards(self, r):
        # somehow unable to modify np.zeros_like
        discounted_r = [0] * len(r)
        running_add = 0
        for t in reversed(range(0, len(r))):
            if r[t] != 0: running_add = 0
            running_add = running_add * self.gamma + r[t]
            discounted_r[t] = running_add
        return np.vstack(discounted_r)

    def batch_training(self, session_name: str, agent: Agent, opponent: Agent, num_batch: int, save_location=None):
        """ 
        mini batch updates
        """
        if session_name == None:
            raise(Exception("Session name is empty, needed for logging games"))
        print(f"Beginning session name: {session_name}")

        all_games = []
        # update weights after every epoch
        for i in range(num_batch):
            print('Training batch #: ', i)
            training_history, game_histories = self.train_epoch(agent, opponent)
            print('Training history: ', training_history.history)
            all_games.extend(game_histories) 

        if save_location:
            self.log_game_histories(game_histories, save_location, session_name)
            self.save_model_and_training_history(agent.model, training_history, save_location)

    def train_epoch(self, training_agent: Agent, op_agent: Agent):
        """
        prints(win rate, total reward, loss)
        returns xs, rewards
        """
        for _ in range(self.epoch):
            engine = Engine(local_ais = {0 : training_agent, 1: op_agent})
            winner = engine.run_game()

        xs, ys, rewards, game_histories = training_agent.get_training_data()
        xs = np.vstack(xs)
        discounted = np.vstack(self.discount_rewards(rewards))
        training_history, game_histories = training_agent.model.fit(xs, discounted)

        # reset stats
        training_agent.reset()
        return training_history, game_histories
    
    def log_game_histories(self, game_histories, location, session_name):
        """
        Logs the game history in file system
        """
        print("Saving game histories to ", location)
        for i in range(len(game_histories)):
            with open(f"{location}/games/{session_name}/{i}", "wb"):
                pickle.dump(game_histories[i])

    def save_model_and_training_history(self, model, training_history, location):
        print("Saving model to ", location)
        model.save(location)
        with open(f"{location}/history", "wb") as fd:
            pickle.dump(training_history.history, fd)
        
    def self_train(self, training_location, hold_location):
        n = 10000
        wins = 0
        for i in range(n):
            print("TRAINING EPISODE: ", i)
            if (i % 1000 == 0):
                self.update_hold(hold_location, training_location)

            engine = Engine(local_ais = {0: KerasAgent(), 
                                1: KerasAgent()})
            winner =  engine.run_game()
            wins += 1 if winner == 0 else 0
            print("WIN RATE: ", wins/(i + 1))
        return wins/n
        
    def evaluate_with_model(self, training_location, eval_model_location, n):
        wins = 0
        for i in range(n):
            engine = Engine(local_ais = {0: KerasAgent(), 
                                1: KerasAgent()})
            winner = engine.run_game()
            wins += 1 if winner == 0 else 0
            print("WIN RATE: ", wins/(i + 1))
        return wins/n

    def benchmark(self, agent: Agent, n=100):
        stats = {}
        # bench marking against other Agents
        opponents = [TaxAgent(), AdversarialAgent()]
        # remove epsilon for benchmarking
        agent.epsilon = 0
        for opponent in opponents: 
            wins = 0
            opponent_name = type(opponent).__name__
            print(f"Benchmarking against {opponent_name}...")
            for i in range(n):
                engine = Engine(local_ais = 
                {0: agent,
                1: opponent})
                winner = engine.run_game()
                wins += 1 if winner == 0 else 0
                win_rate = wins / (i + 1)
            print("Win rate: ", win_rate)
            stats[opponent_name] = win_rate
        print(stats)
        return stats

    def create_checkpoint(self, source, checkpoint_name=None):
        if checkpoint_name == None:
            checkpoint_name = datetime.now().strftime("%Y-%M-%d_%H.%M.%S")
        print('Creating checkpoint at ', checkpoint_name)
        checkpoint_location = f"{self.checkpoints_location}/{checkpoint_name}"
        shutil.copytree(source, checkpoint_location)

if __name__ == "__main__":
    gym = Gym()
    gym.create_checkpoint(gym.training_location)
    asdf
    model = gym.load_model(gym.training_location)
    gym.benchmark(KerasAgent(model))