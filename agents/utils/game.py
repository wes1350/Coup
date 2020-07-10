"""Utilities for extracting information about the game."""

"""Actions"""

def can_income(options):
    return options["Income"]

def can_foreign_aid(options):
    return options["ForeignAid"]

def can_tax(options):
    return options["Tax"]

def can_exchange(options):
    return options["Exchange"]

def steal_targets(options):
    """Note that we should not be able to steal from targets with 0 coins."""
    return options["Steal"]

def assassinate_targets(options):
    return options["Assassinate"]

def coup_targets(options):
    return options["Coup"]

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

def extract_options(options):
    extracted_options = []
    for r in possible_responses(options):
        if isinstance(options[r], bool):
            extracted_options.append(r,)
        else:
            for i in range(len(options[r])):
                extracted_options.append((r, options[r][i]))
    return extracted_options 

