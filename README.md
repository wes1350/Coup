# Coup

### Prerequisites

Configure a Python virtual environment, and then install the following packages:

1. Flask (to run the web server and use any of the Flask extensions below)
2. Flask-SocketIO (for communication between players with the web server)
3. eventlet (to run the web server through SocketIO)
4. Flask-Login (to log in users and if you want to use the database)
5. Flask-SQLAlchemy (for interacting with the database)
6. Flask-Migrate (for updating the database schema)
7. tensorflow, keras (to run KerasAgent)
8. pytorch (to run PytorchAgent)

### Game Structure

Most of the game logic resides in `Engine.py`, with the rest in `State.py`, which `Engine` uses to maintain a representation of the state of a game. `Engine` and `State` both use `Config.py` to set various parameters with respect to how a game is run: for example, what cards to include in the deck, the deck structure, how many coins to give each player, etc. They also make use of the various classes in the `classes/` directory, which represent abstractions of various aspects of a game: players, characters, the deck, etc.

### Running the web server

To play over the browser, we make use of Flask, a popular Python-based web framework. To run over the browser, whether to play against humans, bots, or both, run `python3 app.py`, perhaps with arguments included (e.g. `python3 app.py -s 0.5` to introduce a short delay in bot actions, to avoid game updates from occurring too quickly to understand.) Once the Flask server is started, navigate to `localhost:5000`.

### Agents (bots)

Bots (or agents, as we call them) are found in the `agents/` directory. There are also some files for evaluating agents and training neural network agents, like evaluate_agents.py` and `Gym.py`.

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

Whenever the agent receives a message, it comes in JSON format describing the situation. Consult current agent implementations to see how these are structures (TODO: describe API here.)
 
Furthermore, there are numerous utilities that should help with implementing the above functions for your agent, which can be found in `agents/utils/`.

### Database

`app.db` contains the database file, an SQLite database. To maintain and update the database, we make use of some flask extensions. To get the database up and running, you will need to run `flask db upgrade` on the command line, once all the required packages have been installed, as mentioned above.

The database stores information about registered users and bot types, including their respective ELO scores. 
