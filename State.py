"""Maintains the state of a Coup game. The state includes the Deck of cards, the set of players, and the turn state."""
import time 
import json
from typing import List
from Config import Config
from classes.Player import Player
from classes.Deck import Deck
from classes.Card import Card
from classes.actions.Action import Action
from classes.actions.ForeignAid import ForeignAid
from classes.actions.Tax import Tax
from classes.actions.Steal import Steal
from classes.actions.Exchange import Exchange
from classes.actions.Assassinate import Assassinate
from classes.actions.Income import Income
from classes.actions.Coup import Coup


class State:

    def __init__(self, config : Config, whisper=None, shout=None, get_response=None, local=True, ai_players=[]) -> None:
        """Initialize the game state with players and a deck, then assign cards to each player."""
        self._config = config
        self.whisper = whisper
        self.shout = shout
        self.get_response = get_response
        self.local = local
        self._n_players = config.n_players
        self.ai_players = ai_players
        # Initialize the deck
        self._deck = Deck(self._n_players, config.cards_per_character)
        # Initialize the players and assign them cards from the deck
        unassigned_cards = self._deck.draw(config.cards_per_player * self._n_players)
        self._players = []
        for i in range(self._n_players):
            self._players.append(Player(id_=i, coins=config.starting_coins, 
                                        cards=[unassigned_cards[config.cards_per_player*i+j]
                                               for j in range(config.cards_per_player)]))
        # Penalize the first player in a 2 person game
        if config.penalize_first_player_in_2p_game and self._n_players == 2:
            self._players[0].change_coins(-1 * config.first_player_coin_penalty)

        self._current_player_id = 0

        # Initialize the history
        self._history = []

    def get_n_players(self) -> int:
        return self._n_players

    def get_current_player_id(self) -> int:
        return self._current_player_id

    def update_current_player(self) -> None:
        """Increment the current player id, returning to the first player if appropriate."""
        while True:
            self._current_player_id = (self._current_player_id + 1) % self._n_players
            if self.player_is_alive(self._current_player_id):
                break

    def get_player_cards(self, id_ : int) -> List[Card]:
        return self._players[id_].get_cards()

    def get_player_card(self, player_id : int, card_idx : int) -> Card:
        return self.get_player_cards(player_id)[card_idx]

    def get_player_living_card_ids(self, player_id : int) -> List[int]:
        """Return the indices of the living cards in a player's hand. Note: these are not the ids that the Card objects themselves own."""
        cards = self.get_player_cards(player_id)
        chosen_cards = []
        for i, card in enumerate(cards):
            if card.is_alive():
                chosen_cards.append(i)
        return chosen_cards

    def switch_player_card(self, player_id : int, card_idx : int) -> None:
        """Return the indicated card in the player's hand to the deck, and draw a new one at random."""
        new_card = self._deck.exchange_card(self.get_player_card(player_id, card_idx))
        self._players[player_id].set_card(card_idx, new_card)
        self.whisper("Player {}, your new card {} is {}".format(player_id, card_idx, 
                                                                str(new_card.get_character())), player_id, "info")

    def kill_player_card(self, player_id : int, card_idx : int) -> None:
        self.get_player_card(player_id, card_idx).die()
        if not self.player_is_alive(player_id):
            self.shout("Player {} has been eliminated!".format(player_id))

    def get_player_balance(self, player_id : int) -> int:
        return self._players[player_id].get_coins() 

    def player_is_alive(self, id_ : int) -> bool:
        return self._players[id_].is_alive()

    def n_players_alive(self) -> int:
        statuses = [self.player_is_alive(i) for i in range(self._n_players)]
        return sum([1 for x in statuses if x])
    
    def get_alive_players(self) -> List[int]:
        return [self._players[i].get_id() for i in range(self._n_players) if self.player_is_alive(i)]
    
    def player_must_coup(self, player_id : int) -> bool:
        """Determine whether a player is obligated to coup based on their coin balance."""
        assert 0 <= player_id < self.get_n_players() 
        return self._players[player_id].get_coins() >= self._config.mandatory_coup_threshold

    def player_can_coup(self, player_id : int) -> None:
        """Determine whether a player can afford to coup."""
        assert 0 <= player_id < self.get_n_players() 
        return self._players[player_id].get_coins() >= Coup(None).cost

    def player_can_assassinate(self, player_id : int) -> None:
        """Determine whether a player can afford to assassinate."""
        assert 0 <= player_id < self.get_n_players() 
        return self._players[player_id].get_coins() >= Assassinate(None).cost

    def get_challenge_loser(self, claimed_character : str, actor : int, challenger : int) -> int:
        """Given two players and the claimed character, determine who loses the challenge."""
        living_actor_cards = self.get_player_living_card_ids(actor)
        for id_ in living_actor_cards:
            if self.get_player_card(actor, id_).get_character_type() == claimed_character:
                return challenger
        return actor

    def execute_action(self, player : int, action : Action, ignore_killing : bool = False, 
                       only_pay_cost : bool = False) -> None:
        """Execute a given action and update the game state accordingly. Can involve 
           querying players, e.g. for Exchange. """

        cost = action.cost
        # Sometimes an action was blocked, but the original actor still needs to pay. 
        # In this case, charge them accordingly but don't do anything else.
        if only_pay_cost:
            if action.pay_when_unsuccessful:
                self._players[player].change_coins(-1 * cost)
            return
                    
        target = action.target

        # Handle coin balances
        if action.steal:
            target_player = self._players[target]
            old_balance = target_player.get_coins()
            self._players[target].change_coins(cost)
            # Increase the actor's balance by at most the target's balance
            self._players[player].change_coins(min(old_balance, -1 * cost)) 
        else:
            self._players[player].change_coins(-1 * cost)

        # Check for the case if the affected player has already died this turn
        if not ignore_killing:
            # Handle assassinations, coups
            if action.kill:
                card_id = action.kill_card_id
                self._players[target].kill_card(card_id)

        # Handle exchanging 
        if action.exchange_with_deck:
            n_to_draw = self._config.n_cards_for_exchange
            drawn_cards = self._deck.draw(n_to_draw)
            alive_cards = self.get_player_living_card_ids(player)
            message = "For your exchange, you may choose {} of the following cards:\n    ".format(len(alive_cards))
            options = {"n": len(alive_cards)}
            for i in alive_cards:
                message += " [{}] {} ".format(i, str(self.get_player_card(player, i).get_character()))
                options[i] = str(self.get_player_card(player, i).get_character())
            in_hand = self._config.cards_per_player 
            for i in range(n_to_draw):
                message += " [{}] {} ".format(i + in_hand, str(drawn_cards[i].get_character()))
                options[i + in_hand] = str(drawn_cards[i].get_character())

            cards_to_keep = self.query_exchange(player, in_hand, in_hand + n_to_draw, message + "\n", options)
            
            # Return all cards from our hand we decided not to keep
            returned = []
            for i in range(in_hand):
                if i not in cards_to_keep and i in alive_cards:
                    self._deck.return_card(self.get_player_card(player, i).get_id())
                    returned.append(i)

            # Replace the missing slots with the chosen drawn cards
            return_idx = 0
            for i, card in enumerate(cards_to_keep):
                if in_hand <= card < in_hand + n_to_draw:
                    self._players[player].set_card(returned[return_idx], drawn_cards[card-in_hand])
                    return_idx += 1

            # Return the drawn cards that we didn't keep
            for i, card in enumerate(drawn_cards):
                if i + in_hand not in cards_to_keep:
                    self._deck.return_card(card.get_id())

    def validate_action(self, action : Action, player_id : int, whisper: bool = True) -> bool:
        """Given an action, ensure it can be applied given the game state."""
        # Validate the cost 
        budget = self._players[player_id].get_coins()
        if action.cost > budget:
            if whisper:
                self.whisper("ERROR: not enough coins for action", player_id, "error")
            return False

        # Check if player must Coup
        if self.player_must_coup(player_id):
            if "coup" not in action.aliases:
                return False
        
        # Validate the target, if applicable
        target_id = action.target 
        has_target = target_id is not None
        if has_target:
            # Target must be a valid Player. Bank doesn't count
            if target_id < 0 or target_id >= self.get_n_players():
                if whisper:
                    self.whisper("ERROR: invalid player id", player_id, "error")
                return False 
            # Target must be alive
            if not self.player_is_alive(target_id):
                if whisper:
                    self.whisper("ERROR: chosen player has been eliminated", player_id, "error")
                return False
            # Target must not be self
            if target_id == player_id:
                if whisper:
                    self.whisper("ERROR: cannot target self with action", player_id, "error")
                return False
        
        return True

    def query_exchange(self, player : int, draw_start : int, draw_end : int, prompt_message : str, 
                       options : dict = None) -> List[int]:
        """For an Exchange, prompt the player for which cards they'd like to keep."""
        query_msg = "Pick the cards you wish to keep:\n"
        if not self.local:
            if player in self.ai_players:
                self.whisper(player=player, ai_query_type="exchange", ai_query_options=options)
            else:
                self.whisper(query_msg + prompt_message, player, "prompt")
        while True:
            response = input(query_msg) if self.local else self.get_response(player)
            try: 
                cards = self.translate_exchange(response)
            except ValueError:
                self.whisper("Invalid exchange, please try again.", player, "error")
            else:
                valid = self.validate_exchange(player, cards, draw_start, draw_end)
                if valid:
                    return cards
                self.whisper("Impossible exchange, please try again.", player, "error")

    def translate_exchange(self, response : str) -> List[int]:
        """Given an exchange response, translate it accordingly."""
        response = response.strip()
        return [int(n) for n in response.split(" ")]

    def validate_exchange(self, player : int, cards : List[int], draw_start : int, draw_end : int) -> bool:
        """Given an exchange, ensure it can be done given the game state."""
        alive = self.get_player_living_card_ids(player)
        if len(cards) != len(alive):
            return False
        for i in cards:
            if not (i in alive or draw_start <= i < draw_end):
                return False 
        if len(set(cards)) != len(cards):
            return False
        return True

    def exchange_player_card(self, player : int, character : str) -> None:
        """Given a player and character, find the character in the player's 
           hand and swap it with a new card from the Deck."""
        for id_ in self.get_player_living_card_ids(player):
            if self.get_player_card(player, id_).get_character_type() == character:
                self.switch_player_card(player, id_)
                return
        raise ValueError("Could not find character time among player's living cards") 

    def __str__(self):
        rep = "-"*40
        rep += "{}\n".format("".join([str(p) for p in self._players]))
        return rep

    def masked_rep(self, player : Player):
        rep = "-"*40
        rep += "{}\n".format("".join([str(p) if p.get_id() == player.get_id() 
                                             else p.masked_rep() for p in self._players]))
        return rep

    def broadcast_state(self) -> None:
        """Broadcast the masked state representation to all players."""
        for p in self._players:
            self.whisper(self.masked_rep(p), p.get_id(), "state")
            self.whisper(self.build_state_json(p.get_id()), p.get_id(), "state_json")
            self.whisper(self.build_action_space(p.get_id()), p.get_id(), "action_space")

    def build_action_space(self, player_id : int) -> str:
        actions = {}

        for action in [Income, ForeignAid, Tax, Exchange]:
            actions[str(action())] = self.validate_action(action(), player.get_id())

        for action in [Steal, Assassinate, Coup]:
            targets = [p.get_id() for p in self._players 
                       if (p.get_id() != player_id and 
                           self.validate_action(action(target=p.get_id()), 
                                                player_id, whisper=False))]
            actions[str(action(target=0))] = targets

        return json.dumps(actions)

    def build_state_json(self, player_id : int) -> str:
        state_json = {}
        state_json['currentPlayer'] = self._current_player_id
        state_json['playerId'] = player_id
        state_json['players'] = [p.get_json(mask = p.get_id() != player_id) for p in self._players]
        return json.dumps(state_json)

    def add_to_history(self, event_type : str, event_info : dict) -> None:
        self._history.append((event_type, event_info))
