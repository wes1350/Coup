import socket, os, select, sys, ctypes, time
from ClientMapping import ClientMapping
from _thread import start_new_thread 

class Server:
    MAX_CONNECTIONS = 10
    def __init__(self, server_ip, server_port, start_game_func, read_pipe, write_pipe):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.address = server_ip
        self.port = server_port
        self.client_connections = ClientMapping()
        self.start_game_func = start_game_func
        self.write_pipe = write_pipe
        self.read_pipe = read_pipe
        self.admin = None
        self.running = True
        self.game_started = False

        self.server.bind((self.address, self.port))
        self.server.listen(Server.MAX_CONNECTIONS)
        self.run()

    def run(self) -> None:
        while self.running:
            conn, addr = self.server.accept()
            if self.admin is None:
                self.admin = conn
            print(f"{addr} connected")
            start_new_thread(self.handle_client, (conn, ))
        print('closing server')
        self.terminate_server()

    def send_message(self, conn, message):
        conn.send(message.encode())

    def handle_engine(self):
        print('thread spawned')
        # try to just read from read_pipe
        while(True):
            try:
                message = None
                #message = self.read_pipe.stdout.read().decode()
                with open(self.read_pipe, "r") as f:
                    print('able to open pipe')
                    message = f.read()
                if message:
                    print(message)
                    self.parse_engine_message(message)
            except Exception as e:
                print(e)
                return
            time.sleep(0.01)

    def parse_engine_message(self, message : str):
        """Given a message from the engine, parse it and take the appropriate action."""
        components = message.split(" ")
        if components[0] == "shout":
            self.shout(components[1])
        elif components[0] == "whisper":
            self.whisper(components[2], components[1])
        elif components[0] == "retrieve":
            response = self.client_connections.get_response_from_id(components[1])
            self.answer(response)
        else:
            print("Could not parse engine message: " + message)
            pass

    def handle_client(self, conn):
        self.send_message(conn, "Welcome to Coup! What is your name?")
        first_message = True
        name = None

        while(True):
            #try:
            message = conn.recv(2048).decode()
            if message:
                message = message.rstrip()
                args = message.split(" ")
                if first_message:
                    # Name setting
                    # Don't accept new players once the game has started
                    assert not self.game_started
                    # Make sure player name is unique
                    name = message
                    assert name not in self.client_connections.get_all_names()
                    self.client_connections.add(name, conn, len(self.client_connections))

                    self.shout(f"{name} joined the room!")
                    first_message = False
                elif conn is self.admin and args[0] == "admin":
                    if len(args) > 1:
                        # Admin messages
                        if args[1] == "start_game" and not self.game_started:
                            print('starting new thread here')
                            start_new_thread(self.handle_engine, ())
                            self.game_started = True
                            self.start_game_func()
                            print("Successfully started game")

                        elif args[1] == "terminate_server":
                            self.terminate_server()
                            return
                elif self.game_started:
                    # In-game messages
                    self.client_connections.store(message, conn)
                else:
                    # Pre-game messages
                    message_to_send = f"<{name}>: {message}"
                    self.shout(message_to_send)
            #except Exception as e:
            #    print(e)
            #    self.terminate_conn(conn)
            #    break
            time.sleep(0.01)

    def terminate_server(self):
        print('terminating server')
        self.server.shutdown(socket.SHUT_RDWR) 
        self.server.close()
        self.running = False
    
    def terminate_conn(self, conn):
        print('terminating connection')
        self.client_connections.remove_connection(conn)
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    def whisper(self, message, id_):
        print('whispering')
        conn = self.client_connections.get_connection_from_id(id_)
        if conn:
            try:
                self.send_message(conn, message)
            except Exception as e:
                print(e)
                self.terminate_conn(conn)

    def shout(self, message):
        print('shouting')
        print(self.client_connections)
        for client in self.client_connections.get_all_connections():
            try:
                self.send_message(client, message)
            except Exception as e:
                print(e)
                self.terminate_conn(client)

    def answer(self, message : str) -> str:
        with open(self.write_pipe, "w") as f:
            print('able to open pipe')
            f.write(message)
