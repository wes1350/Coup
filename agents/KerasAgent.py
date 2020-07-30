import os
import random
import itertools
import numpy as np
from keras.utils import to_categorical
from tensorflow import keras

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

class KerasAgent(Agent):
    def __init__(self, label, model=None, epsilon=0, debug=False, verbose=True):
        self.label = label
        self.debug = debug 
        self.verbose = verbose
        self._id = None
        if model is None:
            raise NotImplementedError
        self.model = model
        self.model_input_size = self.model.layers[0].get_config()["batch_input_shape"][1]

        # hyperparameters
        self.epsilon = epsilon 

        self.x_train = []
        self.y_train = []
        self.rewards = []
        self.win = False
        self.game_histories = []
        self.game_history = [] 

        self.state_bit = None
        self.state = None
        self.num_of_players = None
        self.num_of_cards = None
        self.block = None
        self.char_encoding = { 
            'ambassador': 0,
            'assassin': 1,
            'captain': 2,
            'contessa': 3,
            'duke': 4,
            'unknown': 5 }
        self.actions = {
            'income': 0, 
            'foreign_aid': 1, 
            'foreignaid': 1, 
            'tax': 2, 
            'steal': 3, 
            'exchange': 4, 
            'assassinate': 4, 
            'coup': 6}
    
    def __str__(self):
        return f"KerasAgent_{self.label}"

    def log_step(self, input_vector, q):
        # game history is added at event update
        self.x_train.append(input_vector)
        self.y_train.append(q)
        self.append_reward(0)

    def log_game(self, reward):
        # utility function for when a game concludes
        # rewards only appear after game, so need to adjust
        self.rewards = self.rewards[:-1] + [reward]
        self.game_histories.append(self.game_history)
        if self.debug:
            print(self.game_history)
        if self.verbose:
            print("-" * 101 + "\n" + "-" * 45 + " GAME OVER " + "-" * 45 + "\n" + "-" * 101)
        self.game_history = []
        self.win = False
    
    def append_reward(self, reward):
        self.rewards.append(reward)

    def get_training_data(self):
        return (self.x_train, self.y_train, self.rewards, self.game_histories)
    
    def reset(self):
        self.x_train = []
        self.rewards = []
        self.discounted = []
        self.game_history = []
        self.win = False

    def decide_action(self, options):
        possible_moves = self.get_input_vector(options, reactions=None, cards=None, exchanges=None)
        optimal_move, optimal_input, q = self.get_optimal_move(possible_moves)
        self.log_step(optimal_input, q)
        return convert(optimal_move[0], optimal_move[1] if type(optimal_move) != type(True) else None)
        '''
        if assassinate_targets(options):
            return assassinate(random.choice(options["Assassinate"]))
        elif steal_targets(options):
            return steal(random.choice(options["Steal"]))
        else:
            # Sometimes we can't assassinate because we don't have the coins for it,
            # and we can't steal because nobody else has coins to steal. 
            # In this case we tax.
            return tax()
        '''

    def decide_reaction(self, options):
        '''
        possible_inputs = self.get_input_vector(actions=None, reactions=options, cards=None, exchanges=None)
        print(possible_inputs.keys())
        if can_challenge(options):
            return challenge()
        else:
            return block(random.choice(options["Block"]))
        '''
        possible_moves = self.get_input_vector(actions=None, reactions=options, cards=None, exchanges=None)
        optimal_move, optimal_input, q = self.get_optimal_move(possible_moves)
        self.log_step(optimal_input, q)
        return convert(optimal_move[0], optimal_move[1] if optimal_move != True else None)

    def decide_card(self, options):
        '''
        possible_inputs = self.get_input_vector(actions=None, reactions=None, cards=options, exchanges=None)
        print(possible_inputs.keys())
        return random.choice(options)
        '''
        possible_moves = self.get_input_vector(actions=None, reactions=None, cards=options, exchanges=None)
        optimal_move, optimal_input, q = self.get_optimal_move(possible_moves)
        self.log_step(optimal_input, q)
        return optimal_move[0]

    def decide_exchange(self, options):
        # TODO: logic to send the complement
        '''
        possible_inputs = self.get_input_vector(actions=None, reactions=None, cards=None, exchanges=options)
        return choose_exchange_cards(random.sample(options["cards"].keys(), options["n"]))
        '''
        possible_moves = self.get_input_vector(actions=None, reactions=None, cards=None, exchanges=options)
        optimal_move, optimal_input, q = self.get_optimal_move(possible_moves)
        self.log_step(optimal_input, q)
        return choose_exchange_cards([card for card in options['cards'].keys() if card not in optimal_move])

    def update(self, event):
        self.game_history.append(event)
        # this updates the state with new information
        if event["event"] == "state":
            self.state = event["info"]
            if self.num_of_cards == None:
                self.num_of_cards = len(self.state['players'][0]['cards'])
            if self.num_of_players == None:
                self.num_of_players = len(self.state['players'])
            self.state_bit = self.encode_state()
            if self.debug:
                print('Number of cards: ', self.num_of_cards)
                print('Number of players: ', self.num_of_players)
            
        if event["event"] == "winner":
            self.win = event["info"]["winner"] == self._id
            reward = 1 if self.win else -1 
            self.log_game(reward)

        if event["event"] == "block" and event["info"]["to"] == self._id:
            self.block = {
                "from": event["info"]["from"], 
                "as_character": event["info"]["as_character"]
                }
        else:
            # reset block
            self.block = None

    def get_optimal_move(self, possible_moves):
        inputs = [np.array(vector) for vector in possible_moves.values()]
        qs = self.model.predict(np.reshape(inputs, (-1, self.model_input_size)))
        retval_ind = None
        if random.random() < self.epsilon:
            retval_ind = random.choice(range(len(inputs)))
        else:
            retval_ind = np.argmax(qs)
        if self.debug:
            print(qs)
        return (list(possible_moves.keys())[retval_ind], inputs[retval_ind], qs[retval_ind])

    '''
    ---------------------------------------------  ENCODING ------------------------------------------------
    '''
    def get_input_vector(self, actions=None, reactions=None, cards=None, exchanges=None):
        # given a set of actions, reactions, cards, exchanges, return a list of model input vectors 
        retval_dict = {}
        state_vectors = self.state_bit
        empty_action_vectors = self.encode_action(False, None, None)
        empty_reaction_vectors = self.encode_reaction(False, None, None)
        empty_card_vectors = self.encode_card(False, None)
        empty_exchange_vectors = self.encode_exchange(False, None, None)
        if actions:
            for action, targets in actions.items():
                if targets ==  True:
                    retval_dict[(action, targets)] = self.encode_action(True, action, None)
                elif targets == False:
                    continue
                else:
                    for target in targets:
                        retval_dict[(action, target)] = self.encode_action(True, action, target)
            retval_dict = { key: np.concatenate((state_vectors, value, empty_reaction_vectors, empty_card_vectors, empty_exchange_vectors), axis=0) for key, value in retval_dict.items() }
        elif reactions:
            for reaction, as_chars in reactions.items():
                if as_chars == True:
                    retval_dict[(reaction, as_chars)] = self.encode_reaction(True, reaction, None)
                elif as_chars == False:
                    continue
                else:
                    for as_char in as_chars:
                        retval_dict[(reaction, as_char)] = self.encode_reaction(True, reaction, as_char)
            retval_dict = { key: np.concatenate([state_vectors, empty_action_vectors, value, empty_card_vectors, empty_exchange_vectors]) for key, value in retval_dict.items()}
        elif cards:
            retval_dict = { (card, True): self.encode_card(True, card) for card in cards }
            retval_dict = { key: np.concatenate([state_vectors, empty_action_vectors, empty_reaction_vectors, value, empty_exchange_vectors]) for key, value in retval_dict.items()}
        elif exchanges:
            retval_dict = { (card1, card2): self.encode_exchange(True, exchanges["cards"][card1], exchanges["cards"][card2]) for card1, card2 in list(itertools.combinations(exchanges["cards"].keys(), 2)) }
            retval_dict = { key: np.concatenate([state_vectors, empty_action_vectors, empty_reaction_vectors, empty_card_vectors, value]) for key, value in retval_dict.items()}
        else:
            raise NotImplementedError 
        return retval_dict

    def get_char_encoding(self, character) -> int:
        encoding  = self.char_encoding[character.lower()]
        return to_categorical(encoding, len(self.char_encoding))

    def encode_action(self, encoding: bool, action, target):
        bit_length = len(self.actions) + self.num_of_players + 1
        retval = None
        if encoding:
            action_vector = to_categorical(self.actions[action.lower()], len(self.actions))
            if target == None:
                # since players are 0 indexed, and to_categorical starts at 1
                target = self.num_of_players 
            target_vector = to_categorical(target, self.num_of_players + 1)
            retval = np.concatenate([action_vector, target_vector], axis=0)
        else:
            # + 1 to encode no player
            retval = np.zeros(len(self.actions) + self.num_of_players + 1)
        if self.debug:
            print(f"Action encoding({action} {target}): ", retval)
            assert(len(retval) == bit_length)
        return retval

    def encode_reaction(self, encoding: bool, reaction, as_char):
        retval = None
        reactions = {'challenge': 0, 'block': 1, 'pass': 2}
        bit_length = len(reactions) + len(self.char_encoding)
        if encoding:
            reaction_vector = to_categorical(reactions[reaction.lower()], len(reactions))
            as_char = 'unknown' if as_char == None else as_char
            as_char_vector = self.get_char_encoding(as_char)
            retval = np.concatenate([reaction_vector, as_char_vector])
        else:
            retval = np.zeros(len(reactions) + len(self.char_encoding))
        if self.debug:
            print('reaction encoding: ', retval)
            assert(len(retval) == bit_length)
        return retval

    def encode_card(self, encoding: bool, card: int):
        bit_length = self.num_of_cards
        retval = None
        assert(self.num_of_cards != None)
        if encoding:
            retval = to_categorical(card, self.num_of_cards)
        else:
            retval = np.zeros(self.num_of_cards)
        if self.debug:
            print('Card encoding: ', retval)
            assert(len(retval) == bit_length)
        return retval

    def encode_exchange(self, encoding: bool, card1, card2):
        retval = None
        bit_length = len(self.char_encoding) * 2
        if encoding:
            retval = [] 
            retval.extend(self.get_char_encoding(card1))
            retval.extend(self.get_char_encoding(card2))
        else:
            retval = np.zeros(len(self.char_encoding) * 2)
        if self.debug:
            print('Exchange encoding: ', retval)
            assert(len(retval) == bit_length)
        return retval

    def encode_player(self, player):
        bit_length = 1 + (len(self.char_encoding) + 1) * self.num_of_cards
        vector = []
        vector.append([player['coins']])
        for card in player['cards']:
            char = card['character']
            if char == None:
                char = 'unknown'
            vector.append(self.get_char_encoding(char))
            vector.append([1 if card['alive'] else 0])
        retval = np.concatenate(vector)
        if self.debug:
            print('player vector:', retval)
            assert(len(retval) == bit_length)
        return retval
    
    def encode_block(self):
        # TODO: only encode blockable characters only
        # this is set up for only 1:1
        bit_length = len(self.char_encoding)
        vector = []
        if self.block != None:
            vector.append(self.get_char_encoding(self.block['as_character'].lower()))
        else:
            vector = [0] * len(self.char_encoding)
        if self.debug:
            print('block vector:', vector)
            assert(len(vector) == bit_length)
        return np.array(vector)
    
    def encode_state(self):
        """
        player:
            - coin (int)
            - card (# cards)
                - c + 1 bits (c characters, + unknown)
                - 1 bit for alive
        block (1 bit):
            - by (c bits , c for # of characters)
            - by player (n bits)
        """
        vector = [] 
        # first player is always self 
        self._id = self.state['playerId']
        agent = list(filter(lambda x: x['id'] == self._id, self.state['players']))[0]
        opponents = sorted([player for player in self.state['players'] if player['id'] != self._id],
            key=lambda x: x['id'])

        vector.append(self.encode_player(agent))
        vector.extend([self.encode_player(opponent) for opponent in opponents])
        if self.debug:
            print('player vector', vector)

        # block vector
        vector.append(self.encode_block())
        return np.concatenate(vector) 

if __name__ == "__main__":
    # load the saved model
    model = keras.models.load_model("./KerasModel/checkpoint")
    keras_agent = KerasAgent(model)
    start(keras_agent)