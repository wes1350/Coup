import subprocess
import os
from Engine import Engine
from Server import Server
from utils.argument_parsing import parse_args

class Gameroom:
    def __init__(self):
        # need to initiate a server
        #self.read_pipe = subprocess.Popen('md5sum', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        #self.write_pipe = subprocess.Popen('md5sum', stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.server_read_pipe, self.engine_write_pipe = os.pipe()
        self.engine_read_pipe, self.server_write_pipe = os.pipe()
        self.server = Server('localhost', 8080, self.start_game, self.server_read_pipe, self.server_write_pipe)

    def start_game(self):
        # open subprocess to run engine and pass pipe into it
        print('starting the game..')
        self.engine = Engine(self.engine_read_pipe, self.engine_write_pipe)
        print('here in Gameroom')
        self.engine.run_game()

Gameroom()
