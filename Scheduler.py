import configparser
import subprocess
from agents import AdversarialAgent

if __name__ == '__main__':
    '''
        read from agent.conf to spin up agents 
        TODO: configure reaction time
    '''
    config = configparser.ConfigParser()
    config.read('agents.conf')
    agents = [agent_type for agent_type in config['AGENTS']]
    paths = [path for path in config['PATHS']]
    print(paths)
    print(agents)

    for agent in agents:
        if int(config['AGENTS'][agent]) > 0:
            # get path for agent file
            path = config['PATHS'][agent]
            print(path)
            subprocess.run(f"python3 {path}", shell=True, check=True)