# Tarek Chaalan
# @tarekchaalan

"""
This module contains functions for creating a deck of
cards and drawing a card from the deck.
"""

from typing import List, Optional, Tuple
import random

SUITS: List[str] = ["♠", "♥", "♦", "♣"]
RANKS: List[str] = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def create_deck(
    num_decks: int = 8,
    cut_fraction_range: Tuple[float, float] = (0.15, 0.20),
    rng: Optional[random.Random] = None,
) -> List[str]:
    """
    Build a shuffled shoe and apply a rotation "cut".

    - num_decks: number of 52-card decks to combine.
    - cut_fraction_range: choose a cut depth uniformly in this fraction of total size.
      For 8 decks (416 cards), 0.15–0.20 ≈ 62–83 cards from the bottom (close to 60–80).
    - rng: optional random generator for deterministic testing.
    """
    rnd = rng or random
    deck = [f"{rank}{suit}" for _ in range(num_decks) for suit in SUITS for rank in RANKS]
    rnd.shuffle(deck)

    low, high = cut_fraction_range
    low = max(0.0, min(low, 1.0))
    high = max(low, min(high, 1.0))
    depth_from_bottom = max(1, min(len(deck) - 1, int(rnd.uniform(low, high) * len(deck))))
    cut_index = len(deck) - depth_from_bottom
    deck = deck[cut_index:] + deck[:cut_index]
    return deck

def draw_card(deck: List[str]) -> str:
    """Remove and return the next card from the shoe."""
    return deck.pop()