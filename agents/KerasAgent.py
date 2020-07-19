import random
import itertools
import numpy as np
from keras.datasets import mnist
from keras import models
from keras import layers
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
    def __init__(self, model):
        self._id = None
        self.model = model
        self.state_bit = None
        self.state = None
        self.num_of_players = None
        self.num_of_cards = None
        self.char_encoding = { 
            'ambassador': 0,
            'assassin': 1,
            'captain': 2,
            'contessa': 3,
            'duke': 4,
            'unknown': 5 }
        self.actions = {
            income: 0, 
            foreign_aid: 1, 
            tax: 2, 
            steal: 3, 
            exchange: 4, 
            assassinate: 4, 
            coup: 6,
            decline: 7}
        self.blocked = None

    def decide_action(self, options):
        possible_actions = possible_responses(options)
        if assassinate_targets(options):
            return assassinate(random.choice(options["Assassinate"]))
        elif steal_targets(options):
            return steal(random.choice(options["Steal"]))
        else:
            # Sometimes we can't assassinate because we don't have the coins for it,
            # and we can't steal because nobody else has coins to steal. 
            # In this case we tax.
            return tax()

    def decide_reaction(self, options):
        if can_challenge(options):
            return challenge()
        else:
            return block(random.choice(options["Block"]))

    def decide_card(self, options):
        # check each option with the model for the highest prob of winning
        raise NotImplementedError

    def decide_exchange(self, options):
        # decide which 2 to return to deck
        raise NotImplementedError

    def update_state(self, event):
        # this updates the state with new information
        if event["event"] == "state":
            self.state = json.loads(event["info"])
            if self.num_of_cards == None:
                self.num_of_cards = len(self.state['players'][0]['cards'])
                print(self.num_of_cards)
            if self.num_of_players == None:
                self.num_of_players = len(self.state['players'])
                print('Number of players: ', self.num_of_players)
            self.state_bit = self.encode_state()

        if event["event"] == "block" and event["info"]["to"] == self._id:
            self.block = {
                "from": event["info"]["from"], 
                "as_character": event["info"]["as_character"]
                }
        else:
            # reset block
            self.block = None

    '''
    ---------------------------------------------  ENCODING ------------------------------------------------
    '''
    def get_input_vector(self, actions=None, reactions=None, cards=None, exchanges=None):
        # given a set of actions, reactions, cards, exchanges, return a list of model input vectors 
        retval = []
        state_vectors = [self.state_bit]
        empty_action_vectors = [self.encode_action(False, None, None)]
        empty_reaction_vectors = [self.encode_reaction(False, None, None)]
        empty_card_vectors = [self.encode_card(False, None)]
        empty_exchange_vectors = [self.encode_exchange(False, None, None)]
        if actions:
            actions_vectors = []
            for action, targets in actions.items():
                if targets == True:
                    actions_vectors.append(self.encode_action(True, action, None))
                else:
                    for target in targets:
                        actions_vectors.append(self.encode_action(True, action, target)) 
            retval = [np.concatenate(vector) for vector in list(itertools.product(state_vectors, 
            actions_vectors, 
            empty_reaction_vectors, 
            empty_card_vectors, 
            empty_exchange_vectors))]
        elif reactions:
            reaction_vectors = []
            for reaction, as_chars in reactions.items():
                if as_char == True:
                    reaction_vectors.append(self.encode_reaction(True, reaction, None))
                else:
                    for as_char in as_chars:
                        reaction_vectors.append(self.encode_reaction(True, reaction, as_char))
            retval = [np.concatenate(vector) for vector in list(itertools.product(state_vectors, 
            empty_action_vectors, 
            reaction_vectors, 
            empty_card_vectors, 
            empty_exchange_vectors))]
        elif cards:
            card_vectors = [self.encode_card(False, card) for card in cards]
            retval = [np.concatenate(vector) for vector in list(itertools.product(state_vectors, 
            empty_action_vectors, 
            empty_reaction_vectors, 
            card_vectors, 
            empty_exchange_vectors))]
        elif exchanges:
            exchange_vectors = [self.encode_exchange(False, exchanges[card1], exchanges[card2]) for card1, card2 in list(itertools.combinations(exchanges.keys(), 2))]
            retval = [np.concatenate(vector) for vector in list(itertools.product(state_vectors, 
            empty_action_vectors, 
            empty_reaction_vectors, 
            empty_card_vectors, 
            exchange_vectors))]
        else:
            raise NotImplementedError 
        return retval

    def get_char_encoding(self, character) -> int:
        encoding  = self.char_encoding[character.lower()]
        return to_categorical(encoding, len(self.char_encoding))

    def encode_action(self, encoding: bool, action, target):
        if encoding:
            action_vector = to_categorical(self.actions[action], len(self.actions))
            target_vector = to_categorical(target, len(self.num_of_players))
            return np.concatenate([action_vector, target_vector], axis=0)
        else:
            return np.zeros(len(self.actions) + len(self.num_of_players))

    def encode_reaction(self, encoding: bool, reaction, as_char):
        if encoding:
            reactions = {challenge: 0, block: 1}
            reaction_vector = to_categorical(reactions[reaction], len(reactions))
            as_char_vector = to_categorical(self.get_char_encoding(as_char))
            return np.concatenate([reaction_vector, as_char_vector], axis=0)
        else:
            return np.zeros(len(reactions) + len(self.char_encoding))

    def encode_card(self, encoding: bool, card: int):
        assert(self.num_of_cards != None)
        if encoding:
            return to_categorical(card, self.num_of_cards)
        else:
            return np.zeros(self.num_of_cards)

    def encode_exchange(self, encoding: bool, card1, card2):
        if encoding:
            exchange_vector = [] 
            exchange_vector.extend(self.get_char_encoding(card1))
            exchange_vector.extend(self.get_char_encoding(card2))
            return exchange_vector 
        else:
            return np.zeros(len(self.char_encoding) * 2)
    
    def encode_player(self, player):
        vector = []
        vector.append(player['coins'])
        for card in player['cards']:
            vector.append(self.get_char_encoding(card['character'].lower()))
            vector.append(1 if card['character']['alive'] else 0)
        print('player vector:', vector)
        return vector
    
    def encode_block(self):
        # TODO: only encode blockable characters only
        # this is set up for only 1:1
        vector = []
        if self.block != None:
            vector.append(self.get_char_encoding(self.block['as_character'].lower()))
        else:
            vector = [0] * len(self.char_encoding)
            assert(vector == [0, 0, 0, 0, 0])
        print('block vector:', vector)
        return vector
    
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
        
        [not implemented]
        challenge(1 bit)
            - by player (n bits)

        our action:
        need to encode action space
            - income
            - foreign aid
            - tax
            - steal (n bits where n players can steal)
            - assassinate (n bits in to include target)
            - exchange (2* c bits for the 2 cards returned)
            - pass
            - block (c bits)
            - challenge (1 bit)
        """
        vector = [] 
        # first player is always self 
        self._id = self.state['playerId']
        agent = self.state['players'].filter(lambda x: x['id'] == self._id )
        opponents = sorted([player for player in self.state['players'] if player['id'] != self._id],
            key=lambda x: x['id'])

        vector.append(self.encode_player(agent))
        vector.extend([self.encode_player(opponent) for opponent in opponents])
        print('player vector', vector)

        # block vector
        vector.append(self.encode_block())
        return np.ndaray.flatten(np.array(vector))

if __name__ == "__main__":
    keras_agent = KerasAgent(None)
    start(keras_agent)
    