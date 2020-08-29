import sys
sys.path.insert(0, '..')  # For importing app config, required for using db
from datetime import datetime
import os
import pickle
import json
import numpy as np
import shutil
from keras import models, layers
from tensorflow import keras
from coup.Engine import Engine
from coup.agents import *

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
        # model location should relative to /KerasModel
        model = None
        try:
            print(model_location)
            print("Loading model from ", model_location)
            model = keras.models.load_model(model_location)
            print("Loaded model")
        except Exception as e:
            print("Unable to load model")
            raise(e)
        return model

    def load_checkpoint(self, checkpoint_name):
        location = f"{self.checkpoints_location}/{checkpoint_name}"
        return self.load_model(location)

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
            location = f"{save_location}/{session_name}"
            self.log_game_histories(game_histories, location)
            self.save_model_and_training_history(agent.model, training_history, location)

        return agent

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
        training_history = training_agent.model.fit(xs, discounted)

        # reset stats
        training_agent.reset()
        return training_history, game_histories

    def log_game_histories(self, game_histories, location):
        """
        Logs the game history in file system
        """
        print("Saving game histories to ", location)
        for i in range(len(game_histories)):
            dir = f"{location}/games"
            if not os.path.exists(dir):
                os.makedirs(dir)
            with open(f"{dir}/{i}", "wb") as fd:
                pickle.dump(game_histories[i], fd)

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

    def self_train_with_blending(self, training_location, hold_location, blending_agents, blending_ratio=0.2):
        # sample blending_ratio, if true, play a blending agent ar random, else self train
        raise NotImplementedError

    def evaluate_with_model(self, training_location, eval_model_location, n):
        wins = 0
        for i in range(n):
            engine = Engine(local_ais = {0: IncomeAgent(),
                                1: IncomeAgent()})
            winner = engine.run_game()
            wins += 1 if winner == 0 else 0
            print("WIN RATE: ", wins/(i + 1))
        return wins/n

    def benchmark(self, agent: Agent, n=100):
        stats = {}
        # bench marking against other Agents
        opponents = [TaxAgent(), IncomeAgent(), AdversarialAgent(), HonestAgent(), StrategicAgentV1(), TrickyAgent()]
        # remove epsilon for benchmarking
        agent.epsilon = 0
        agent.verbose = False
        for opponent in opponents:
            wins = 0
            opponent_name = str(opponent)
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
    print('imported')
    gym = Gym()
    '''
    trained_agent = KerasAgent(label='training', model=gym.load_model(gym.training_location), verbose=False)
    checkpoint_agent = KerasAgent(label='checkpoint', model=gym.load_checkpoint('checkpoint'), verbose=False)
    batch_training_agent = KerasAgent(label='bathTraining1', model=gym.load_checkpoint('testBatchTraining'), verbose=False)
    benchmark_stats = {}
    benchmark_stats['training'] = gym.benchmark(trained_agent)
    benchmark_stats['testBatchTraining'] = gym.benchmark(batch_training_agent)

    # self train with blending against existing AIs
    session_name = "testBatchTraining1"
    trained_agent = gym.batch_training(session_name, trained_agent, AdversarialAgent(), 100, gym.checkpoints_location)

    benchmark_stats['checkpoint'] = gym.benchmark(checkpoint_agent)
    benchmark_stats[session_name] = gym.benchmark(trained_agent)
    print(json.dumps(benchmark_stats, indent=4))

    '''
