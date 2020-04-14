import socket
import os
import select
import sys
import ctypes
from ClientMapping import ClientMapping
from _thread import start_new_thread 

class Server:
    MAX_CONNECTIONS = 10
    def __init__(self, server_ip, server_port, start_game_func, read_pipe, write_pipe):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server = server
        self.address = server_ip
        self.port = server_port
        self.client_connections = ClientMapping()
        self.start_game_func = start_game_func
        self.write_pipe = write_pipe
        self.read_pipe = read_pipe
        self.admin = None
        self.running = True
        self.game_started = False

        server.bind((self.address, self.port))
        server.listen(Server.MAX_CONNECTIONS)
        self.run()

    def run(self) -> None:
        while self.running:
            conn, addr = self.server.accept()
            if (self.admin == None):
                self.admin = conn
            self.client_connections[conn] = {"name": None}
            print(f"{addr} connected")
            start_new_thread(self.handle_client, (conn, addr))
        print('closing server')
        self.terminate_server()

    def send_message(self, conn, message):
        conn.send(message.encode())

    def handle_engine(self):
        print('thread spawned')
        # try to just read from read_pipe
        while(True):
            try:
                #message = self.read_pipe.stdout.read().decode()
                with open(self.read_pipe, "r") as f:
                    print('able to open pipe')
                    message = f.read()
                if message:
                    print(message)
                    self.broadcast(message, self.server)
            except Exception as e:
                print(e)
                return;

    def parse_engine_messages(self, message):
        pass

    def handle_client(self, conn, addr):
        self.send_message(conn, "Welcome to the coup game! What is your name?")
        first_message = True
        name = None

        while(True):
            try:
                message = conn.recv(2048).decode()
                if message:
                    message = message.rstrip()
                    args = message.split(" ")
                    # set name
                    if first_message:
                        self.client_connections.set_conn_name(conn, message)
                        name = message
                    if (conn == self.admin and args[0] == "admin"):
                        # this is a command
                        if args[1] == "start_game" and not self.game_started:
                            print('starting new thread here')
                            start_new_thread(self.handle_engine, ())
                            self.game_started = True
                            self.start_game_func()

                        elif args[1] == "terminate_server":
                            self.terminate_server()
                            return;
                    else:
                        if first_message:
                            message_to_send = f"{name} joined the room!"
                            self.broadcast(message_to_send, conn)
                            first_message = False
                        else:
                            message_to_send = f"<{name}>: {message}"
                            self.broadcast(message_to_send, conn)
            except Exception as e:
                print(e)
                self.terminate_conn(conn)
                break;

    def terminate_server(self):
        print('terminating server')
        self.server.shutdown(socket.SHUT_RDWR) 
        self.server.close()
        self.running = False;
    
    def terminate_conn(self, conn):
        print('terminating connection')
        self.client_connections.remove_conn(conn)
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    def whisper(self, message, name):
        print('whispering')
        conn = self.client_connections.get_conn(name)
        if conn:
            self.send_message(conn, message)

    def broadcast(self, message, conn=None):
        print('broadcasting')
        print(self.client_connections)
        for client in self.client_connections.get_all_conns():
            if client != conn:
                try:
                    self.send_message(client, message)
                except Exception as e:
                    print(e)
                    self.terminate_conn(client)
