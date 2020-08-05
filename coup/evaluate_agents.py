import sys, random
sys.path.insert(0, '..')  # For importing app config, required for using db
from coup.Engine import Engine
from coup.models import DEFAULT_ELO  # Must use relative import here to avoid db error
from coup.utils.elo_utils import calculate_new_elos, get_agent_elos, update_agent_elos
from coup.agents.TrickyAgent import TrickyAgent
from coup.agents.RandomAgent import RandomAgent
from coup.agents.HonestAgent import HonestAgent
from coup.agents.MimickingAgent import MimickingAgent
from coup.agents.TaxAgent import TaxAgent
from coup.agents.AdversarialAgent import AdversarialAgent

def run_match(agents, elos=None, randomize_order=True, n_iters=1000, use_default_elos=False):
    if elos is None:
        if use_default_elos:
            elos = [DEFAULT_ELO] * len(agents)
        else:
            raise ValueError("Must specify initial elos or specify to use default elos")
    old_elos = [elo for elo in elos]
    print("Agents:", str([str(agent) for agent in agents]).replace("'",""))
    print("Old elos:", [round(elo) for elo in old_elos])

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
            print(f"Win proportions after game {i+1}:", [round(win_tracker[j]/(i+1), 3) for j in range(len(win_tracker))])

        elos = calculate_new_elos(elos, agent_order[winner])

    print("Final win proportions:", [win_tracker[i]/n_iters for i in range(len(win_tracker))])
    print("New elos:", [round(elo) for elo in elos])
    elo_diffs = [elos[i] - old_elos[i] for i in range(len(elos))]
    elo_diffs = [("+" if diff >= 0 else "") + str(round(diff)) for diff in elo_diffs]
    print("Elo changes:", str(elo_diffs).replace("'",""))
    return elos


if __name__ == "__main__":
    a = TrickyAgent(0.5)
    b = HonestAgent()
    c = RandomAgent()
    d = TaxAgent()
    e = TrickyAgent(0.8)
    f = AdversarialAgent()

    agents = [a, b, c, d, e, f]
    elos = get_agent_elos(agents)
    n_iters = 1000
    new_elos = run_match(agents, elos=elos, n_iters=n_iters)
    update_agent_elos(agents, new_elos, [n_iters] * len(agents))
