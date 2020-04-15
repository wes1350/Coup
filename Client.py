import socket
import select
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if len(sys.argv) != 3:
    print("Correct usage: script, IP ADD, port number")
    exit()
IP_ADD = str(sys.argv[1])
PORT = int(sys.argv[2])
server.connect((IP_ADD, PORT))

def send_message(conn, message):
	conn.send(message.encode())
try:
    while True:
        sockets_list = [sys.stdin, server]
        read_sockets, write_socket, error_socket = select.select(sockets_list, [server], [])
        for sock in read_sockets:
            if sock is server:
                try:
                    message = sock.recv(2048).decode()
                    print(message)
                except Exception as e:
                    print(e)
                    break
            else:
                message = sys.stdin.readline()
                send_message(server, message)
                sys.stdout.write("You: ")
                sys.stdout.write(message)
                sys.stdout.flush()
except KeyboardInterrupt:
    server.close()

