import socket
import select
import sys
from _thread import start_new_thread 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if len(sys.argv) != 3:
    print("Correct usage: script, IP add, port number")
    exit()

IP_ADD = str(sys.argv[1])
PORT = int(sys.argv[2])

server.bind((IP_ADD, PORT))

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
        if client == conn:
            try:
                send_message(conn, message)
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


        

                                 

