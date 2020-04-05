
class Action:
    def __init__(**kwargs):
        self._properties = {
            "take_coins_target_id": None,
            "kill": False, 
            "kill_target_id": None,  # player id we are killing
            "kill_target_card_idx": None,
            "actor": None,  # what card we are claiming, e.g. Duke for Tax
            "cost": None,
            "is_blockable": False,  # improve the following later
            "blockable_by": None
        }
        
        for arg in kwargs:
            self.properties[arg] = kwargs[arg]
