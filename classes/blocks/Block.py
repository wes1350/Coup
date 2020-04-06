class Block:
    def __init__(self, **kwargs):
        self.properties = {
            "from_player": None,
            "from_character": None 
        }   

    def get_property(self, prop : str):
        return self._properties[prop]

    def set_property(self, prop : str, value):
        self._properties[prop] = value
