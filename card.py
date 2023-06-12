""" 
This module contains the functions related to the card. 
"""


def get_card_value(card, current_hand_value):
    """
    This function returns the value of the card.
    """
    rank = card[:-1]
    if rank in ["K", "Q", "J"]:
        return 10
    if rank == "A":
        if current_hand_value + 11 <= 21:
            return 11
        return 1
    return int(rank)
