# Tarek Chaalan
# tchaalan23@csu.fullerton.edu
# @tarekchaalan

"""
This file contains the functions that run the game.
"""
from termcolor import colored
from ui import (
    show_title,
    render_table,
    deal_animation,
    flash_message,
)
from card import get_card_value
from deck import draw_card, create_deck
import sys
import time
import platform
import os
if platform.system() != 'Windows':
    import termios
    import tty
from typing import List, Dict, Any
from collections import deque


def print_slowly(text, delay=0.05):
    use_tty_effects = platform.system() != 'Windows' and sys.stdin.isatty()
    if use_tty_effects:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(sys.stdin.fileno())
    try:
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay if sys.stdin.isatty() else 0)
        print()
    finally:
        if use_tty_effects:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def input_slowly(prompt, delay=0.05):
    use_tty_effects = platform.system() != 'Windows' and sys.stdin.isatty()
    if use_tty_effects:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(sys.stdin.fileno())
    try:
        for char in prompt:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay if sys.stdin.isatty() else 0)
    finally:
        if use_tty_effects:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if os.environ.get("BJ_AUTOPLAY") == "1":
        lower = prompt.lower()
        if "choose an action" in lower:
            # Configurable autoplay actions
            # BJ_ACTIONS: comma-separated sequence, e.g., h,s,h
            # BJ_ACTION: single fallback action (h/s/d)
            if not hasattr(input_slowly, "_autoplay_actions"):
                seq = os.environ.get("BJ_ACTIONS", "").strip()
                actions = [a.strip() for a in seq.split(",") if a.strip()]
                setattr(input_slowly, "_autoplay_actions", deque(actions))
            actions_deque = getattr(input_slowly, "_autoplay_actions")
            if actions_deque:
                return actions_deque.popleft()
            return os.environ.get("BJ_ACTION", "s")
        return ""
    return input()

def colorize_player_card(card):
    """Return a colored, bold version of the card number."""
    return colored(card, 'green', attrs=['bold'])

def colorize_dealer_card(card):
    """Return a colored, bold version of the card number."""
    return colored(card, 'red', attrs=['bold'])

def colorize_other(card):
    """Return a colored, bold version of the card number."""
    return colored(card, 'cyan', attrs=['bold'])

def ensure_deck_cards(deck: List[str], minimum: int = 60) -> bool:
    """
    Ensure the deck has at least `minimum` cards; extend with a new shoe if low.
    Returns True if a new shoe was added.
    """
    if len(deck) < minimum:
        deck.clear()  # Clear remaining cards for a true reshuffle
        deck.extend(create_deck())
        return True
    return False

def draw_from_shoe(deck: List[str]) -> tuple[str, bool]:
    """
    Draw a card, replenishing the shoe if needed.
    Returns (card, reshuffled) where reshuffled is True if a new shoe was added.
    """
    reshuffled = ensure_deck_cards(deck)
    return draw_card(deck), reshuffled

def deal_initial_cards(player, deck, is_dealer=False):
    """
    This function deals the initial cards to the player.
    Returns (player, reshuffled) where reshuffled is True if deck was reshuffled.
    """
    card1, reshuffled1 = draw_from_shoe(deck)
    card2, reshuffled2 = draw_from_shoe(deck)
    player["hand"] = [card1, card2]
    player["cardvalue"] = get_hand_value(player["hand"])
    player["doubled"] = False
    player.pop("status", None)

    # UI rendering will be handled by caller through deal_animation

    return player, (reshuffled1 or reshuffled2)


def get_hand_value(hand):
    """
    Calculate the value of a hand of cards.
    """
    value = 0
    aces = 0

    # First, add up the value of the non-ace cards and count the aces.
    for card in hand:
        if card[:-1] == "A":
            aces += 1
        else:
            value += get_card_value(card, value)

    # Then, add the aces, treating them as 11 if possible, and 1 otherwise.
    for _ in range(aces):
        if value + 11 <= 21:
            value += 11
        else:
            value += 1

    return value


def play_player_turn(player, deck, on_update=None, on_reshuffle=None):
    """
    This function runs the player's turn.
    """
    while True:
        if player["cardvalue"] == 21:
            player["status"] = "blackjack"
            flash_message(f"{player['name']} BLACKJACK!")
            if on_update:
                on_update()
            break
        if player["cardvalue"] > 21:
            player["status"] = "bust"
            flash_message(f"{player['name']} BUSTS!")
            if on_update:
                on_update()
            break

        action = input_slowly("Choose an action: (H)it, (S)tand, or (D)ouble: ")
        player["doubled"] = False

        if action.lower() == "h":
            card, reshuffled = draw_from_shoe(deck)
            if reshuffled and on_reshuffle:
                on_reshuffle()
            player["hand"].append(card)
            player["cardvalue"] = get_hand_value(player["hand"])
            player["status"] = "hit"
            if on_update:
                on_update()
        elif action.lower() == "d":
            if player["bet"] <= player["chips"]:
                card, reshuffled = draw_from_shoe(deck)
                if reshuffled and on_reshuffle:
                    on_reshuffle()
                player["hand"].append(card)
                player["cardvalue"] = get_hand_value(player["hand"])
                player["chips"] -= player[
                    "bet"
                ]  # Subtract additional bet from player's chips
                player["bet"] *= 2  # Double the bet
                player["doubled"] = True
                player["status"] = "double"
                if on_update:
                    on_update()
                break
            print_slowly("Not enough chips to double. Please choose another action.")
        elif action.lower() == "s":
            player["status"] = "stand"
            if on_update:
                on_update()
            break
        else:
            print_slowly("Invalid action. Please try again.")


def play_dealer_turn(dealer_hand, deck, on_update=None, on_reshuffle=None):
    """
    This function runs the dealer's turn.
    """
    # Reveal the second card and show current value
    # UI layer handles rendering; just maintain values
    if on_update:
        on_update()

    while True:
        if dealer_hand["cardvalue"] >= 17 and dealer_hand["cardvalue"] <= 21:
            dealer_hand["status"] = "stand"
            if on_update:
                on_update()
            break
        if dealer_hand["cardvalue"] > 21:
            dealer_hand["status"] = "bust"
            if on_update:
                on_update()
            break
        card, reshuffled = draw_from_shoe(deck)
        if reshuffled and on_reshuffle:
            on_reshuffle()
        dealer_hand["hand"].append(card)
        dealer_hand["cardvalue"] = get_hand_value(dealer_hand["hand"])
        dealer_hand["status"] = "hit"
        if on_update:
            on_update()


def evaluate_hand(player, dealer_hand):
    """
    This function evaluates the player and dealer's hands
    """
    # UI layer prints table; here we only compute results and set status

    if player["cardvalue"] > 21:
        player["status"] = "bust"
    elif player["cardvalue"] == dealer_hand["cardvalue"]:
        player["status"] = "push"
        player["chips"] += player["bet"]
    elif player["cardvalue"] == 21 and len(player["hand"]) == 2:
        player["status"] = "blackjack"
        player["chips"] += player["bet"] * 2
    elif player["cardvalue"] > dealer_hand["cardvalue"] and player["doubled"]:
        player["status"] = "win-double"
        player["chips"] += player["bet"] * 2  # Double the winnings if player doubled
    elif (
        player["cardvalue"] > dealer_hand["cardvalue"] or dealer_hand["cardvalue"] > 21
    ):
        player["status"] = "win"
        player["chips"] += player["bet"] * 2
    elif player["cardvalue"] < dealer_hand["cardvalue"]:
        player["status"] = "lose"
