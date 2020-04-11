Coup platform

Requirements:

client <> server
1) input
2) output (state)

State:
- everyone's cards
- status of everyone's cards
- whose turn it is
- how much money everyone has
- actions on current turn

[does not need to include history]

Input:
- actions (e.g. tax)
- reactions (e.g. block a steal)

Output:
[partial reflection of the state or query for an action/reaction]

API Contract:
Send a command to ask about the state
- Print the state while keeping private info hidden
(or ask for specifics)


questions:
how does the server keep track of that interaction between client <> server

GameState:
# public
- 
{
    players: List<Player>,
    currentTurn: {
        currentPlayer: int # playerId
        actionsTaken: OrderedList<Action>[]
    }
    get_representation()
}

Action: {
    playerTo: int?,
    playerFrom: int,
    move: int 
}

Player {
    playerId: int
    money: int
    faceUpCards: List<Card>
    faceDownCards: List<Card>
}

GameEngine:
{
    main() # contains all the game logic

    updateCurrentTurnState() # Call during the turn
    updateGameState() # Call once the turn is over 
    
    requestPlayerAction(playerId) # ask player for input
    processPlayerAction(Action) 
}

Character:
- contessa, assassin, ambassador, captain, duke

Contessa: Card:
{
    ability: function(state) -> state 
}

# private
- each player's unrevealed cards
- cards in the deck and their order


Preliminary Game Structure:
- Command line interface
- all players share the same terminal 



engine runs, and sends output/queries input through server calls
server.shout/whisper -> send to players and continue execution

server.ask -> wait for response and then process

Gameroom
--- start server, wait for clients 
--- when everyone joins
----- run command start Engine(Server)

- server maintains {client_address : player_id} (and reverse?)

Server: 
	server.shout(msg)
	server.whisper(msg, player)
	server.ask(msg, players)
	server._responses : store responses from clients
	server.get_responses()
	server.clear_responses() - engine will send this to server once it determines all messages look good. That way engine doesn't access old responses from previous asks.

engine.server.ask("Challenge?", players 1-5)
server receives ask
server sends requests to each player

server continually receives responses
when receiving a response:
- server._responses[client] = response

meanwhile:
engine: 
- while(True):
--- check server.responses for new responses
--- for all responses, if a response is bad: server.ask() again
--- if all responses look good
------ terminate, move onto processing responses
--- else
------ sleep(0.001)


