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
    return "s " + str(target)

def assassinate(target):
    return "a " + str(target)

def coup(target):
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

def choose_exchange(cards):
    """cards is a list of card choices"""
    return " ".join(cards)
