"""An Agent with a basic strategy."""

import sys, random

if "." not in __name__:
    from utils.game import *
    from utils.network import *
    from Agent import Agent
else:
    from .utils.game import *
    from .utils.network import *
    from .Agent import Agent


class StrategicAgentV1(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.my_living_chars = None
        self.coin_balances = None
        self.alive_counts = None
        self.my_id = None
        self.dead_chars = None
        self.tag = "1"

        # game state tracking
        self.last_action_character = None
        self.last_block_character = None

        self.character_priority = ["Captain", "Duke", "Assassin", "Contessa", "Ambassador"]

    def get_honest_actions(self):
        actions = []
        for char in characters_to_moves:
            if self.my_living_chars[char] > 0:
                actions += characters_to_moves[char]["action"]
        return actions

    def get_honest_blocks(self):
        blocks = []
        for char in characters_to_moves:
            if self.my_living_chars[char] > 0:
                blocks += characters_to_moves[char]["block"]
        return blocks

    def get_most_ahead_opponent(self):
        most_alive = max([self.alive_counts[id_] for id_ in self.alive_counts if id_ != self.my_id])
        players_with_most_alive = [id_ for id_ in self.alive_counts if self.alive_counts[id_] == most_alive and id_ != self.my_id]
        most_ahead_opponent = players_with_most_alive[0]
        highest_coin_count = self.coin_balances[most_ahead_opponent]
        for player in players_with_most_alive[1:]:
            if self.coin_balances[player] > highest_coin_count:
                highest_coin_count = self.coin_balances[player]
                most_ahead_opponent = player

        return most_ahead_opponent

    def n_players_alive(self):
        return len([p for p in self.alive_counts if self.alive_counts[p] > 0])

    def update(self, event):
        e = event["event"]
        info = event["info"]
        if e == "state":
            state_info = extract_state_info(event)
            self.my_living_chars = state_info["my_living_characters"]
            self.coin_balances = state_info["coin_balances"]
            self.alive_counts = state_info["alive_counts_by_player"]
            self.my_id = state_info["my_id"]
            self.dead_chars = state_info["dead_characters"]
        elif e == "action_resolution":
            # Clear turn storage variables at the end of a turn
            self.last_action_character = None
            self.last_block_character = None
        elif e == "action":
            self.last_action_character = info["as_character"]
        elif e == "block":
            self.last_block_character = info["as_character"]


    def decide_action(self, options):
        honest_actions = self.get_honest_actions()
        if can_assassinate(options) and "Assassinate" in honest_actions:
            target = self.get_most_ahead_opponent()
            if target in assassinate_targets(options):
                return assassinate(target)
        if can_coup(options):
            return coup(self.get_most_ahead_opponent())
        if can_tax(options) and "Tax" in honest_actions:
            return tax()
        if can_steal(options) and "Steal" in honest_actions:
            target = self.get_most_ahead_opponent()
            if target in coup_targets(options):
                return steal(self.get_most_ahead_opponent())
        if can_exchange(options) and "Exchange" in honest_actions:
            return exchange()
        if self.n_players_alive() > 2:
            return income()
        else:
            return foreign_aid()

    def decide_reaction(self, options):
        character_sums = {c: self.my_living_chars[c] + self.dead_chars[c] for c in self.dead_chars}
        if options["Challenge"]:
            if self.last_block_character is not None:
                # Challenging a block
                if character_sums[self.last_block_character] == 3:
                    return challenge()
                elif self.n_players_alive == 2 and \
                     character_sums[self.last_block_character] == 2 and \
                     self.last_block_character == "Contessa":
                    return challenge()
            else:
                # Challenging an action
                if character_sums[self.last_action_character] == 3:
                    return challenge()
                elif self.n_players_alive == 2 and \
                    character_sums[self.last_action_character] == 2 and \
                    self.last_block_character in ["Duke", "Captain"]:
                    return challenge()


        honest_blocks = self.get_honest_blocks()
        for char in options["Block"]:
            if char in honest_blocks:
                return convert("Block", char)

        return decline()

    def decide_card(self, options):
        # Choose the card corresponding to the character with lowest priority
        priorities = [self.character_priority.index(options[c]) for c in options]
        response = priorities.index(max(priorities))
        if response not in options:
            raise ValueError("Invalid card choice:", str(response), "with options", str(options))
        return response

    def decide_exchange(self, options):
        cards = []
        priorities = [self.character_priority.index(options["cards"][c]) for c in options["cards"]]
        for i in range(int(options["n"])):
            cards.append(list(options["cards"].keys())[priorities.index(min(priorities))]) # min to choose highest priority
            priorities.pop(list(options["cards"].keys()).index(cards[-1]))
        if len(cards) == 2:
            if cards[0] == cards[1]:
                cards[1] += 1 # account for bug with above pop when choosing multiple cards where indices might be the same
        elif len(cards) > 2:
            raise ValueError("Exchange choice not properly implemented for more than 2 cards in a hand")
        response = choose_exchange_cards(cards)
        for c in cards:
            if c not in options["cards"]:
                raise ValueError("Invalid exchange choice:", str(response), "with options:", str(options))
        return response

if __name__ == "__main__":
    start(StrategicAgentV1(), sys.argv[1])

