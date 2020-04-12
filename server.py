import socket
import select
import sys
from _thread import start_new_thread 

class Server:

def __init__(self, server_ip, server_port):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	self.server = server
	self.address = server_ip
	self.port = server_port
	server.bind((self.server, self.port))

# max connections
server.listen(10)

# dict[conn] -> name
client_connections = {}

def send_message(conn, message):
    conn.send(message.encode())

def handle_client(conn, addr):
    send_message(conn, "Welcome to the coup game!")

    while(True):
        try:
            message = conn.recv(2048)
            if message:
                message_to_send = f"<{addr}>: {message.decode()}"
                print(message_to_send)
                broadcast(message_to_send, conn)
            else:
                remove(conn)
        except:
            continue

def broadcast(message, conn):
    for client in client_connections:
        print(client)
        if client != conn:
            try:
                send_message(client, message)
            except:
                client.close()
                remove(client)

def remove(conn):
    client_connections.pop(conn)

while True:
    conn, addr = server.accept()
    client_connections[conn] = ""
    print(f"{addr} connected")
    start_new_thread(handle_client, (conn, addr))

conn.close()
server.close()


        

                                 

