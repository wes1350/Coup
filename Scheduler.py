import time
import socketio
import threading
import configparser
import subprocess
from agents import AdversarialAgent

if __name__ == '__main__':
    '''
        read from agent.conf to spin up agents 
    '''
    config = configparser.ConfigParser()
    config.read('agents.conf')
    agents = [agent_type for agent_type in config['AGENTS']]
    paths = [path for path in config['PATHS']]

    def run_agent(path):
        try:
            subprocess.run(f"python3 {path}", shell=True, check=False)
            print('done')
        except BaseException:
            pass

    thread_pool = []
    for agent in agents:
        num_agents = int(config['AGENTS'][agent])
        for i in range(num_agents):
            # get path for agent file
            path = config['PATHS'][agent]
            print(f"Spinning up {agent}") 
            thread = threading.Thread(target=run_agent, args=(path,))
            thread_pool.append(thread)
            thread.start()

    sio = socketio.Client()
    sio.connect('http://localhost:5000')

    @sio.event
    def connect():
        print("Observer connected!")

        # takes time for agents to connect
        wait = 4
        for i in range(wait - 1, 0, -1):
            time.sleep(1)
            print(f"Game starts in {i}...")
        sio.emit("start_observer")

    @sio.event
    def disconnect():
        print('observer disconnecting...')
        sio.disconnect()

    # send start signal
    connect()
    
    # wait for threads to finish
    for thread in thread_pool:
        thread.join()

    print('all agents exited')
    disconnect()
    exit()
