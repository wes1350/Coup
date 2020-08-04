"""Reads a configuration from agent.conf to automatically spin up agents."""
import time, socketio, threading, configparser, subprocess, os, sys

if len(sys.argv) != 2:
    raise Exception("Must specify room to schedule bots in")
room = sys.argv[1]

file_dir = os.path.dirname(os.path.realpath(__file__)) 

config = configparser.ConfigParser()
print(file_dir + '/agents/agents.conf')
config.read(file_dir + '/agents/agents.conf')
agents = [agent_type for agent_type in config['AGENTS']]
paths = [path for path in config['PATHS']]
total_agents = sum([int(config['AGENTS'][agent]) for agent in agents])

sio = socketio.Client()

def run_agent(path, room):
    try:
        subprocess.run(f"python3 {file_dir}/{path} {room}", shell=True, check=False)
        print('done')
    except BaseException:
        pass

@sio.event
def connect():
    print("Connected as observer")
    sio.emit("observer_connect", room)

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
        thread = threading.Thread(target=run_agent, args=(path, room))
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
