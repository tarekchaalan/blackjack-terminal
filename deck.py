"""
This module contains functions for creating a deck of 
cards and drawing a card from the deck.
"""

import random
from random import shuffle


def create_deck():
    """
    This function creates a deck of cards.
    """
    deck = []
    suits = ["♠", "♥", "♦", "♣"]
    ranks = 8 * ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    for suit in suits:
        for rank in ranks:
            deck.append(rank + suit)
    shuffle(deck)
    cut = random.randint(len(deck) - 80, len(deck) - 60)
    deck = deck[cut:] + deck[:cut]
    return deck


def draw_card(deck):
    """
    This function draws a card from the deck and removes it from the deck
    """
    return deck.pop()
