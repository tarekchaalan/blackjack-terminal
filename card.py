# Tarek Chaalan
# @tarekchaalan

"""
This module contains the functions related to the card.
"""

from typing import Optional

FACE_CARD_VALUES = {"K": 10, "Q": 10, "J": 10}

def get_card_value(card: str, current_hand_value: int = 0) -> int:
    """
    Return the numeric value of a card.

    - For non-ace ranks: J/Q/K → 10, numeric ranks → their integer value.
    - For aces: returns 11 if it does not bust given current_hand_value, else 1.

    current_hand_value is expected to be the running total of the hand so far,
    excluding any aces not yet evaluated.
    """
    rank = card[:-1]
    if rank in FACE_CARD_VALUES:
        return 10
    if rank == "A":
        return 11 if current_hand_value + 11 <= 21 else 1
    try:
        return int(rank)
    except ValueError as exc:
        raise ValueError(f"Invalid card rank: {rank!r} in card {card!r}") from exc

def get_count_value(card: str) -> int:
    """
    Return the card counting value for Hi-Lo system (inverted).
    
    2-6: -1
    7-9: 0
    10-A: +1
    """
    rank = card[:-1]
    
    # 2-6 cards
    if rank in ["2", "3", "4", "5", "6"]:
        return -1
    
    # 7-9 cards
    if rank in ["7", "8", "9"]:
        return 0
    
    # 10, J, Q, K, A cards
    if rank in ["10", "J", "Q", "K", "A"]:
        return 1
    
    return 0
