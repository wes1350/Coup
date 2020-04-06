class Reaction:
    def __init__(self, **kwargs):
        self._properties = {
            "reaction_type": None,
            "from_player": None
        }

        for arg in kwargs:
            self._properties[arg] = kwargs[arg]

    def get_property(self, prop : str):
        return self._properties[prop]

    def set_property(self, prop : str, value):
        self._properties[prop] = value
