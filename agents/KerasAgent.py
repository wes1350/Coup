import random
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
        self.model = model
        # state here represents players cards, coins
        self.state = None
        self.char_encoding = { 
            'ambassador': 0,
            'assassin': 1,
            'captain': 2,
            'contessa': 3,
            'duke': 4 }
        
    def get_char_encoding(self, character) -> int:
        return self.char_encoding[character.lower()]

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

    def update_state(self, event):
        if event["event"] == "state":
            self.state = json.loads(event["info"])
    
    def state_to_bits(self, options):
        """
        player:
            - coin (int)
            - card (# cards)
                - c + 1 bits (c characters, + unknown)
                - 1 bit for alive
        block (1 bit):
            - by (c bits , c for # of characters)
            - by player (n bits)
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
            
            - block (c bits)
            - challenge (1 bit)
        """
        raise NotImplementedError

if __name__ == "__main__":
    # load the model
    (train_images, train_labels), (test_images, test_labels) = mnist.load_data()

    network = models.Sequential()
    network.add(layers.Dense(784, activation='relu', input_shape=(28 * 28,)))
    network.add(layers.Dense(784, activation='relu', input_shape=(28 * 28,)))

    network.add(layers.Dense(10, activation='softmax'))

    network.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    train_images = train_images.reshape((60000, 28*28))
    trains_images = train_images.astype('float32') / 255
    test_images = test_images.reshape((10000, 28*28))
    test_images = test_images.astype('float32') / 255

    train_labels = to_categorical(train_labels)
    test_labels = to_categorical(test_labels)

    network.fit(train_images, train_labels, epochs=1, batch_size=256)

    test_loss, test_acc = network.evaluate(test_images, test_labels)
    network.save('./keras_model')
    print('test_acc: ', test_acc, 'test_loss', test_loss)
    model = keras.models.load_model('./keras_model')
    keras_agent = KerasAgent(model)
    start(on_action=keras_agent.decide_action, on_reaction=keras_agent.decide_reaction, 
          on_card=keras_agent.decide_card, update_f=keras_agent.update_state)
    