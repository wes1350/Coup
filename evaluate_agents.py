import random 
from Engine import Engine
from agents.TrickyAgent import TrickyAgent
from agents.RandomAgent import RandomAgent
from agents.HonestAgent import HonestAgent
from agents.MimickingAgent import MimickingAgent
from agents.TaxAgent import TaxAgent
from agents.AdversarialAgent import AdversarialAgent
from app import db
from models import AgentType, User, DEFAULT_ELO

def run_match(agents, elos=None, randomize_order=True, n_iters=1000):
    if elos is None:
        elos = [1000 for _ in range(len(agents))]

    print("Old elos:", elos)
    agent_order = [i for i in range(len(agents))]
    win_tracker = {}
    for i in range(len(agents)):
        win_tracker[i] = 0

    for i in range(n_iters):
        if randomize_order:
            random.shuffle(agent_order)
        local_ais = {}
        for j in range(len(agents)):
            local_ais[j] = agents[agent_order[j]]
        engine = Engine(local_ais=local_ais)
        winner = engine.run_game()
        win_tracker[agent_order[winner]] += 1
        if (i + 1) % 100 == 0:
            print("Win proportions:", [win_tracker[i]/n_iters for i in range(len(win_tracker))])
            print(f"Game {i + 1} finished")

        elos = calculate_new_elos(elos, agent_order[winner])
        # elos = calculate_new_elos([elos[i] for i in agent_order], winner)
    print("New elos:", elos)
    print("Win proportions:", [win_tracker[i]/n_iters for i in range(len(win_tracker))])
    print("-------")
    return elos

def calculate_new_elos(elos, winner):
    def calculate_pair_elo_change(winner_elo, loser_elo):
        """Algorithm and terminology taken from Wikipedia's article on ELO"""
        K = 10
        rating_diff = winner_elo - loser_elo
        q_ratio = 10**(rating_diff/400)
        e_winner = 1/(1 + 1/q_ratio)
        e_loser = 1/(1 + q_ratio)
        winner_update = K * (1 - e_winner)
        loser_update = K * (0 - e_loser)
        return (winner_update, loser_update)
        
    # Calculate ELO change between each (winner, loser) pair. 
    # The winner elo will change as much as the loser elos combined.
    new_elos = []
    total_winner_change = 0
    for i in range(len(elos)):
        if i == winner:
            new_elos.append(elos[i])
        else:
            winner_change, loser_change = calculate_pair_elo_change(elos[winner], elos[i])
            total_winner_change += winner_change
            new_elos.append(elos[i] + loser_change)
    new_elos[winner] += total_winner_change
    return new_elos

def get_db_elos(agents):
    elos = []
    for _, agent in enumerate(agents):
        db_entry = AgentType.query.filter(AgentType.name == str(agent)).first()
        if db_entry is None:
            db.session.add(AgentType(name=str(agent)))
            db.session.commit()
            elos.append(DEFAULT_ELO)
        else:
            elos.append(db_entry.elo)
    
    return elos

def update_db_elos(agents, elos, n_games_per_agent):
    if len(agents) != len(elos) or len(agents) != len(n_games_per_agent):
        raise ValueError("agent, elo, and n_game lists must be equal in length")
    
    for i, agent in enumerate(agents):
        db_entry = AgentType.query.filter(AgentType.name == str(agent)).first()
        db_entry.set_elo(elos[i])
        db_entry.add_games(n_games_per_agent[i])
    
    db.session.commit()


if __name__ == "__main__":
    a = TrickyAgent(0.5)
    b = HonestAgent()
    c = RandomAgent()
    d = TaxAgent()
    e = MimickingAgent()
    f = AdversarialAgent()

    agents = [a, b, c, d, e, f]

#     elos = [1000 for i in range(len(agents))]
    elos = get_db_elos(agents)

    # run_match([a, b])
    # run_match([b, a])
    # run_match([a, a])
    # run_match([b, b])
    print("Got from db:", get_db_elos(agents))
    n_iters = 300
    new_elos = run_match(agents, elos=elos, n_iters=n_iters)
    update_db_elos(agents, new_elos, [n_iters for i in range(len(agents))])
    print("Stored in db:", get_db_elos(agents))
    # run_match([b, b, b])



