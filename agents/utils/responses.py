"""Functions corresponding to responses to the Game Engine."""

"""Actions"""

def income():
    return "I"

def foreign_aid():
    return "f"

def tax():
    return "t"

def exchange():
    return "e"

def steal(target):
    assert target is not None
    return "s " + str(target)

def assassinate(target):
    assert target is not None
    return "a " + str(target)

def coup(target):
    assert target is not None
    return "c " + str(target)

"""Reactions"""

def decline():
    return "n"

def block(as_character):
    return "b " + as_character

def challenge():
    return "c"

"""Card Selection"""

def choose_card(card):
    return str(card)

def choose_exchange_cards(cards):
    """cards is a list of card choices"""
    return " ".join(cards)

"""Misc"""

def convert(string, identifier=None):
    name = string.lower().strip()
    if name == "income":
        return income()
    elif name in ["foreign_aid", "foreignaid", "foreign aid"]:
        return foreign_aid()
    elif name == "tax":
        return tax()
    elif name == "exchange":
        return exchange()
    elif name == "steal":
        return steal(identifier)
    elif name == "assassinate":
        return assassinate(identifier)
    elif name == "coup":
        return coup(identifier)
    elif name in ["pass", "decline"]:
        return decline()
    elif name == "block":
        return block(identifier)
    elif name == "challenge":
        return challenge()
    else:
        assert isinstance(string, str)
        raise ValueError("Unrecognized value to convert " + string)
