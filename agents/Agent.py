"""Base class for AI agents."""

class Agent:
    def __init__(self):
        pass

    def decide_action(self, actions : dict):
        """Given possible actions, choose an action to do."""
        raise NotImplementedError()

    def decide_card(self):
        raise NotImplementedError()

    def decide_exchange(self):
        raise NotImplementedError()

    def decide_reaction(self):
        raise NotImplementedError()

    def update(self, update) -> None:
        """Given an update event, update the internal state to account for it."""
        pass
