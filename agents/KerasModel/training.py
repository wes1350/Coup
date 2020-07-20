import random
import numpy as np
from keras.datasets import mnist
from keras import models
from keras import layers
from keras.utils import to_categorical
from tensorflow import keras

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

model = models.Sequential()
model.add(layers.Dense(units=200, input_dim=70, activation='relu', kernel_initializer='glorot_uniform'))