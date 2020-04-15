import os
import time

def engine_write_pipe(read_pipe, write_pipe, message):
    # send
    os.write(write_pipe, message.encode())
    # wait for ack
    while True:
        message = os.read(read_pipe, 1024)
        if message.decode() == "ack":
            return;
        time.sleep(0.1)

def engine_read_pipe(read_pipe):
    message = os.read(read_pipe, 2048).decode()
    return message
