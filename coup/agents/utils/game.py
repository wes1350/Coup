"""Utilities for extracting information about the game."""

"""Functions corresponding to responses to the Game Engine."""

"""Actions"""

def income():
    return "Income"

def foreign_aid():
    return "ForeignAid"

def tax():
    return "Tax"

def exchange():
    return "Exchange"

def steal(target):
    assert target is not None
    return "Steal " + str(target)

def assassinate(target):
    assert target is not None
    return "Assassinate " + str(target)

def coup(target):
    assert target is not None
    return "Coup " + str(target)

"""Reactions"""

def decline():
    return "N"

def block(as_character):
    return "Block " + as_character

def challenge():
    return "Challenge"

"""Card Selection"""

def choose_card(card):
    return str(card)

def choose_exchange_cards(cards):
    """cards is a list of card choices"""
    return " ".join([str(i) for i in cards])

"""Functions determining possible responses"""

"""Actions"""

def can_income(options):
    return options["Income"]

def can_foreign_aid(options):
    return options["ForeignAid"]

def can_tax(options):
    return options["Tax"]

def can_exchange(options):
    return options["Exchange"]

def can_steal(options):
    return len(steal_targets(options)) > 0

def can_assassinate(options):
    return len(assassinate_targets(options)) > 0

def can_coup(options):
    return len(coup_targets(options)) > 0

def steal_targets(options):
    """Note that we should not be able to steal from targets with 0 coins."""
    return options["Steal"]

def assassinate_targets(options):
    return options["Assassinate"]

def coup_targets(options):
    return options["Coup"]

def requires_target(action):
    if action in ["Steal", "Assassinate", "Coup"]:
        return True
    elif action in ["Income", "Foreign Aid", "ForeignAid", "Tax", "Exchange"]:
        return False
    else:
        raise ValueError(f"{action} is not a valid action string")

"""Reactions"""

def can_challenge(options):
    return options["Challenge"]

def block_options(options):
    return options["Block"]

def can_pass(options):
    return options["Pass"]

"""Card Selection"""

"""Exchange Selection"""

"""Misc"""

def possible_responses(options):
    return [r for r in options if options[r]]

def extract_options(options, option_type):
    if option_type in ["action", "reaction"]:
        extracted_options = []
        for r in possible_responses(options):
            if isinstance(options[r], bool):
                extracted_options.append((r, None))
            else:
                for i in range(len(options[r])):
                    extracted_options.append((r, options[r][i]))
        return extracted_options
    elif option_type == "card_selection":
        return [c for c in options]
    elif option_type == "exchange":
        n = options["n"]
        if n == 1:
            return [(c, options["cards"][c]) for c in options["cards"]]
        elif n == 2:
            extracted_options = []
            cards = options["cards"]
            for a in cards:
                for b in cards:
                    if b > a:
                        extracted_options.append([(a, cards[a]), (b, cards[b])])
            return extracted_options

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

