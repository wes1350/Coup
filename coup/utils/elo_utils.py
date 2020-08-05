from coup import db  # importing directly from __init__ will not access the proper db and make changes ephemeral
from coup.models import AgentType, DEFAULT_ELO  # Must use relative import here to avoid db error

def get_agent_elo(agent):
    db_entry = AgentType.query.filter(AgentType.name == str(agent)).first()
    if db_entry is None:
        db.session.add(AgentType(name=str(agent)))
        db.session.commit()
        return DEFAULT_ELO
    else:
        return db_entry.elo

def get_agent_elos(agents):
    return [get_agent_elo(agent) for agent in agents]

def update_agent_elo(agent, elo, n_games, commit=True):
    # agent can be an Agent or its string representation
    db_entry = AgentType.query.filter(AgentType.name == str(agent)).first()
    db_entry.set_elo(elo)
    db_entry.add_games(n_games)

    if commit:
        db.session.commit()

def update_agent_elos(agents, elos, n_games_per_agent, groupby_agent=True):
    if len(agents) != len(elos) or len(agents) != len(n_games_per_agent):
        raise ValueError("agent, elo, and n_games lists must be equal in length")

    # If the same agent is present more than once, average its updated elos
    # Otherwise the default implementation stores the last given occurrence of the agent
    if groupby_agent:
        grouped_agents = {}
        for i, agent in enumerate(agents):
            if str(agent) not in grouped_agents:
                grouped_agents[str(agent)] = [i]
            else:
                grouped_agents[str(agent)].append(i)

        def average_list_over_indices(list_, indices):
            return sum([list_[idx] for idx in indices])/len(indices)

        for agent_name in grouped_agents:
            update_agent_elo(agent_name,
                             average_list_over_indices(elos, grouped_agents[agent_name]),
                             average_list_over_indices(n_games_per_agent, grouped_agents[agent_name]),
                             commit=False)

    else:
        # Default behavior, does not account for case when an agent is present more than once
        for i in range(len(agents)):
            update_agent_elo(agents[i], elos[i], n_games_per_agent[i], commit=False)

    db.session.commit()

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
