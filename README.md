# Coup

### Coup Rules

This repository tries as best as possible to implement the rules described [here](https://www.ultraboardgames.com/coup/game-rules.php).

### Prerequisites

Configure a Python virtual environment, and then run `pip install -r requirements.txt`.

### Game Structure

Most of the game logic resides in `Engine.py`, with the rest in `State.py`, which `Engine` uses to maintain a representation of the state of a game. `Engine` and `State` both use `Config.py` to set various parameters with respect to how a game is run: for example, what cards to include in the deck, the deck structure, how many coins to give each player, etc. They also make use of the various classes in the `classes/` directory, which represent abstractions of various aspects of a game: players, characters, the deck, etc.

### Running the web server

To play over the browser, we make use of Flask, a popular Python-based web framework. To run over the browser, whether to play against humans, bots, or both, run `python3 app.py`, perhaps with arguments included (e.g. `python3 app.py -s 0.5` to introduce a short delay in bot actions, to avoid game updates from occurring too quickly to understand.) Once the Flask server is started, navigate to `localhost:5000`.

### Agents (bots)

Bots (or agents, as we call them) are found in the `agents/` directory. There are also some files for evaluating agents and training neural network agents, like `evaluate_agents.py` and `Gym.py`.

To test agents against each other without a human player (e.g. when evaluating agent strength), make use of Engine's `local_ais` parameter. From there it is easy: import instantiate the desired agents, and pass them into Engine, e.g.:

    # imports...
    a = TrickyAgent(0.5)
    b = HonestAgent()
    c = AdversarialAgent()
    engine = Engine(local_ais={0: a, 1: b, 2: c})
    winner = engine.run_game()

Refer to `evaluate_agents.py` for a more in-depth example.

#### Implementing an Agent

To implement an `Agent`, you need to extend the `Agent` class and implement 5 functions, explained below. Technically, you can omit their implementations to use a default implementation, but you will likely want to replace them with something more intelligent. You can always refer to the structure of some of the existing agents to get a better idea of how this is done.

The 5 functions are:

1. `update` to update the agent's state upon receiving an event update
2. `decide_action` to give a response when it's the agent's turn to do an `Action`, e.g. Tax
3. `decide_reaction` to give a response when it's the agent's turn to do a `Reaction`, e.g. Block
4. `decide_card` to give a response when the agent must choose a card to lose e.g. when Assassinated
5. `decide_exchange` to give a response when the agent must choose which cards to keep during an Exchange action

Whenever the agent receives a message, it comes in dictionary format describing the situation. Consult the API section below to see how these are structured. You can also take a look at current agent implementations to see how they interact with messages. Furthermore, there are numerous utilities that should help with implementing the above functions for your agent, which can be found in `agents/utils/`, and are used extensively throughout the various `Agent` implementations.

#### Agent API

There are two broad classes of messages agents receive during a game: *event updates*, which update the agent on the progression of the game, and *response queries*, which prompt the agent to return a response of some kind. Also note that players are indexed from 0, i.e. in a four player game, the players have indices [0, 1, 2, 3], corresponding to turn order.

##### Event Updates

In general, the agent should update its internal state (if it has one, as intelligent agents should) upon receiving an informative event update message. This is done using the `update` function, #1 in the list above. Given the event, the agent updates its internal state appropriately.

The possible event update messages are given below. Each is in the form of a dictionary with two keys: `event`, which describes the event type, and `info`, which describes the corresponding information. Below, the event name for each event type is given, along with a description of the info.

- `state`: describes, from the agent's point of view, the visible state of the game. This includes the agent's player index, the index of the current player, and the coin balance, index, and cards of each player (if visible).
- `action`: describes a chosen action by a player
- `action_resolution`: describes whether the previous action was successful
- `block`: describes a chosen block by a player
- `block_resolution`: describes whether the previous block was successful
- `challenge`: describes a chosen challenge by a player
- `challenge_resolution`: describes whether the previous challenge was successful
- `card_swap`: describes when a player swaps a card (the characters involved are only visible to the agent involved in the swap)
- `draw`: describes when a player draws a card during an Exchange (the characters involved are only visible to the agent involved in the swap)
- `card_loss`: describes when a player loses an influence and what card they reveal
- `winner`: describes the player who wins the game
- `loser`: describes a player who has been eliminated


##### Response Queries

Of course, the agent must be able to act when required to. To do so, it must be able to handle the situations described in #2-#5 in the list above. In each case, the agent is presented with a data structure describing what options it has available to it, which describe all possible legal moves in some format. From these options, the agent must decide what action to take. Below, the `options` data structure, the sole parameter to each of the `decide_xxxxx` functions, is described for each situation.

For return values, make use of the provided utilities in `agents/utils/game.py`. For example, `return tax()` to Tax, `return convert("Block", "Duke")` to block as a Duke, and `return choose_exchange_cards([1, 3])` to select the cards with indices `1` and `3` during an Exchange.

`decide_action`: a dictionary containing each action and whether it is possible (if it does not accept a target) or what targets it can be applied to (if it requires a target). For example:

    {
        "Income": true,
        "ForeignAid": true,
        "Tax": true,
        "Exchange": true,
        "Steal": [1],
        "Assassinate": [],
        "Coup": []
    }

`decide_reaction`: the same format as the `decide_action` options dictionary, except with the corresponding options. For blocks, the possible choices are the characters that can be used to block. For example, in response to a `Steal` action:

    {
        "Block": ["Ambassador", "Captain"],
        "Challenge": true,
        "Pass": true
    }

`decide_card`: a dictionary containing the cards that can be chosen when losing an influence (i.e. a card is lost.) with their corresponding indices. For example:

    {
        0: "Contessa",
        1: "Assassin"
    }

The index of the desired card should be returned.

`decide_exchange`: a dictionary describing how many cards can be chosen (in the `n` field) and what characters the possible cards correspond to. For example:

    {
        "n": 1,
        "cards": {
            "1": "Captain",
            "2": "Duke",
            "3": "Contessa"
        }
    }

To return a response, use `return choose_exchange_cards([cards])`, where `[cards]` is a list of card indices of the appropriate length.

#####

### Database

`app.db` contains the database file, an SQLite database. To maintain and update the database, we make use of some flask extensions. To get the database up and running, you will need to run `flask db upgrade` on the command line, once all the required packages have been installed, as mentioned above.

The database stores information about registered users and bot types, including their respective ELO scores.
