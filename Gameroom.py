import subprocess
import os
from Engine import Engine
from Server import Server

class Gameroom:
    def __init__(self):
        # need to initiate a server
        #self.read_pipe = subprocess.Popen('md5sum', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        #self.write_pipe = subprocess.Popen('md5sum', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.read_pipe, self.write_pipe = os.pipe()
        self.server = Server('localhost', 8080, self.start_game, self.read_pipe, self.write_pipe)

    def start_game(self):
        # open subprocess to run engine and pass pipe into it
        print('starting the game..')
        self.engine = Engine(self.read_pipe, self.write_pipe)
        print('here')

Gameroom()
