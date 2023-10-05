# Tarek Chaalan
# tchaalan23@csu.fullerton.edu
# @tarekchaalan

"""
This file contains the functions that run the game.
"""
from termcolor import colored
from card import get_card_value
from deck import draw_card
import sys
import time
import termios
import tty

def print_slowly(text, delay=0.05):
    """
    Print out the text in a typewriter fashion.
    """
    # Disable echoing of characters
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(sys.stdin.fileno())

    try:
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def input_slowly(prompt, delay=0.05):
    # Disable echoing of characters
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(sys.stdin.fileno())

    try:
        for char in prompt:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

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

def deal_initial_cards(player, deck, is_dealer=False):
    """
    This function deals the initial cards to the player.
    """
    card1 = draw_card(deck)
    card2 = draw_card(deck)
    player["hand"] = [card1, card2]
    player["cardvalue"] = get_hand_value(player["hand"])

    if not is_dealer:
        print_slowly(
            player["name"]
            + " has "
            + colorize_player_card(card1)
            + " and "
            + colorize_player_card(card2)
            + " ("
            + colorize_other(str(player["cardvalue"]))
            + ")"
        )
    else:
        print_slowly("\nDealer has " + colorize_dealer_card(card1) + (" and an") + colorize_dealer_card(" unknown card"))

    return player


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


def play_player_turn(player, deck):
    """
    This function runs the player's turn.
    """
    while True:
        if player["cardvalue"] == 21:
            print_slowly("Blackjack!")
            break
        if player["cardvalue"] > 21:
            print_slowly("Bust!")
            break

        action = input_slowly("Choose an action: (H)it, (S)tand, or (D)ouble: ")
        player["doubled"] = False

        if action.lower() == "h":
            card = draw_card(deck)
            player["hand"].append(card)
            player["cardvalue"] = get_hand_value(player["hand"])
            print_slowly(
                player["name"]
                + " hits and receives "
                + colorize_player_card(card)
                + " ("
                + colorize_other(str(player["cardvalue"]))
                + ")"
            )
        elif action.lower() == "d":
            if player["bet"] <= player["chips"]:
                card = draw_card(deck)
                player["hand"].append(card)
                player["cardvalue"] = get_hand_value(player["hand"])
                player["chips"] -= player[
                    "bet"
                ]  # Subtract additional bet from player's chips
                player["bet"] *= 2  # Double the bet
                player["doubled"] = True
                print_slowly(
                    player["name"]
                    + " Doubles and receives "
                    + colorize_player_card(card)
                    + ". Bet is now "
                    + str(player["bet"])
                    + " ("
                    + colorize_other(str(player["cardvalue"]))
                    + ")"
                )
                break
            print_slowly("Not enough chips to double. Please choose another action.")
        elif action.lower() == "s":
            break
        else:
            print_slowly("Invalid action. Please try again.")


def play_dealer_turn(dealer_hand, deck):
    """
    This function runs the dealer's turn.
    """
    # Reveal the second card
    dealer_card_values = [
        get_card_value(card, dealer_hand["cardvalue"]) for card in dealer_hand["hand"]
    ]
    print_slowly(
        "Dealer reveals his second card: "
        + colorize_dealer_card(dealer_hand["hand"][1])
        + " ("
        + colorize_other(str(sum(dealer_card_values)))
        + ")"
    )

    while True:
        if dealer_hand["cardvalue"] >= 17 and dealer_hand["cardvalue"] <= 21:
            print_slowly(dealer_hand["name"] + " stands with (" + colorize_other(str(dealer_hand["cardvalue"])) + ")")
            break
        if dealer_hand["cardvalue"] > 21:
            print_slowly(dealer_hand["name"] + " busts")
            break
        card = draw_card(deck)
        dealer_hand["hand"].append(card)
        dealer_hand["cardvalue"] = get_hand_value(dealer_hand["hand"])
        print_slowly(
            dealer_hand["name"]
            + " hits and receives "
            + colorize_dealer_card(card)
            + " ("
            + colorize_other(str(dealer_hand["cardvalue"]))
            + ")"
        )


def evaluate_hand(player, dealer_hand):
    """
    This function evaluates the player and dealer's hands
    """
    print_slowly(
        player["name"]
        + "'s Hand: "
        + colorize_player_card(str(player["hand"]))
        + "  ("
        + colorize_other(str(player["cardvalue"]))
        + ")"
    )

    if player["cardvalue"] > 21:
        print_slowly("Bust!\n")
    elif player["cardvalue"] == dealer_hand["cardvalue"]:
        print_slowly("Push!\n")
        player["chips"] += player["bet"]
    elif player["cardvalue"] == 21 and len(player["hand"]) == 2:
        print_slowly("Blackjack!\n")
        player["chips"] += player["bet"] * 2
    elif player["cardvalue"] > dealer_hand["cardvalue"] and player["doubled"]:
        print_slowly("Won with a Double!\n")
        player["chips"] += player["bet"] * 2  # Double the winnings if player doubled
    elif (
        player["cardvalue"] > dealer_hand["cardvalue"] or dealer_hand["cardvalue"] > 21
    ):
        print_slowly("Win!\n")
        player["chips"] += player["bet"] * 2
    elif player["cardvalue"] < dealer_hand["cardvalue"]:
        print_slowly("Lose!\n")
