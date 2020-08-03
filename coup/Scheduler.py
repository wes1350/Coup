import time
import socketio
import threading
import configparser
import subprocess
from coup.agents import AdversarialAgent

if __name__ == '__main__':
    """
        read from agent.conf to spin up agents
    """
    config = configparser.ConfigParser()
    config.read('agents/agents.conf')
    agents = [agent_type for agent_type in config['AGENTS']]
    paths = [path for path in config['PATHS']]
    total_agents = sum([int(config['AGENTS'][agent]) for agent in agents])

    sio = socketio.Client()

    def run_agent(path):
        try:
            subprocess.run(f"python3 {path}", shell=True, check=False)
            print('done')
        except BaseException:
            pass

    @sio.event
    def connect():
        print("Connected as observer")
        sio.emit("observer_connect")

    @sio.event
    def disconnect():
        print('Disconnected as observer')
        sio.disconnect()

    thread_pool = []
    for agent in agents:
        num_agents = int(config['AGENTS'][agent])
        for _ in range(num_agents):
            # get path for agent file
            path = config['PATHS'][agent]
            print(f"Spinning up {agent}")
            thread = threading.Thread(target=run_agent, args=(path,))
            thread_pool.append(thread)
            thread.start()

    sio.connect('http://localhost:5000')

    # send start signal
    sio.emit("start_observer", total_agents)

    # wait for threads to finish
    for thread in thread_pool:
        thread.join()

    print('all agents exited')
    disconnect()
    exit()
