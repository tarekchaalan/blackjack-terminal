#! /usr/bin/env python3

# Tarek Chaalan
# tchaalan23@csu.fullerton.edu
# @tarekchaalan

"""
This is a text-based blackjack game, played in the terminal.
"""

from termcolor import colored
import json
import sys
import time
import termios
import tty

from game import (
    deal_initial_cards,
    play_player_turn,
    play_dealer_turn,
    evaluate_hand,
)
from deck import create_deck

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

def load_player_data():
    """
    Load player data from JSON file.
    """
    try:
        with open("player_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_player_data(data):
    """
    Save player data to JSON file.
    """
    with open("player_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file)


def get_player_chip_balance(players, player_name):
    """
    Get player's chip balance from saved data
    """
    if player_name in players:
        return players[player_name]
    return 10000.00


def display_chips(players):
    """
    Display the current chip balances of players with chips greater than 0.
    """
    print("\n__________________________________________________\n")
    print_slowly("\nCurrent Chip Balances:")
    players_with_chips = False
    for player in players:
        if player["chips"] > 0:
            print_slowly(player["name"] + " - Chips: " + str(player["chips"]))
            players_with_chips = True
        else:
            topup = input_slowly(
                player["name"]
                + " is out of chips, an anonymous donor is offering you $10,000,"
                + " would you like to accept? (y/n): "
            )
            while topup.lower() not in ["y", "n"]:
                print_slowly("Invalid input. Please enter 'y' or 'n'.\n")
                print_slowly(
                    player["name"]
                    + " is out of chips, an anonymous donor is offering you $10,000,"
                    + " would you like to accept? (y/n): "
                )
            if topup.lower() == "y":
                player["chips"] = 10000
                print_slowly(player["name"] + " - Chips: " + str(player["chips"]))
                players_with_chips = True
    return players_with_chips


def get_player_names(player_count):
    """
    Get the names of all the players.
    """
    players = load_player_data()
    game_players = []
    print_slowly("\n")
    for i in range(player_count):
        player_name = input_slowly("Enter player " + str(i + 1) + "'s name: ")
        game_players.append(
            {
                "name": player_name,
                "chips": get_player_chip_balance(players, player_name),
            }
        )
    return game_players


def get_valid_bet_amount(player):
    """
    Prompt the player for their bet amount and validate it.
    """
    while True:
        if player["chips"] == 0:
            return 0
        try:
            bet = float(input_slowly(f"{player['name']}, enter your bet amount: "))
            if 0 < bet <= player["chips"]:
                return bet
            print_slowly("Invalid bet amount. Please enter a valid bet.")
        except ValueError:
            print_slowly("Invalid input. Please enter a valid bet amount.")


def get_player_count():
    """
    Prompt the user for the number of players and validate it.
    """
    while True:
        print("__________________________________________________\n")
        try:
            player_count = int(input_slowly("Enter the number of players: "))
            if player_count >= 1:
                return player_count
            print_slowly("\nInvalid number of players. Please try again.")
        except ValueError:
            print_slowly("\nInvalid input. Please enter a valid number of players.")


def get_bet_and_active_players(players):
    """
    Prompt the players for their bet amounts and remove players with no chips.
    """
    print_slowly("\n")
    players_still_playing = []
    for player in players:
        bet = get_valid_bet_amount(player)
        if bet == 0:
            continue  # Skip to the next player without adding them to players_still_playing
        player["bet"] = bet
        player["chips"] -= bet
        players_still_playing.append(player)
    print("\n__________________________________________________")
    return players_still_playing


def deal_and_play_turns(players, deck, dealer_name):
    """
    Deal the initial cards and play the player and dealer turns.
    """
    print_slowly("\n")
    for player in players:
        deal_initial_cards(player, deck)
    dealer_hand = deal_initial_cards({"name": dealer_name}, deck, True)
    # Player turns
    for player in players:
        print_slowly("\n" + player["name"] + "'s turn (" + colorize_other(str(player["cardvalue"])) + ")")
        play_player_turn(player, deck)
    # Dealer's turn
    print_slowly("\nDealer's turn")
    play_dealer_turn(dealer_hand, deck)
    return dealer_hand


def evaluate_results_and_ask_continue(players, dealer_hand):
    """
    Evaluate the results and ask the user if they want to continue.
    """
    print("\n__________________________________________________\n")
    print_slowly("\nResults:\n")
    print_slowly(
        dealer_hand["name"]
        + "'s Hand: "
        + colorize_dealer_card(str(dealer_hand["hand"]))
        + "  ("
        + colorize_other(str(dealer_hand["cardvalue"]))
        + ")\n"
    )
    for player in players:
        evaluate_hand(player, dealer_hand)
    print("__________________________________________________")
    play_again = input_slowly("\nDo you want to play again? (y/n): ")
    while play_again.lower() not in ["y", "n"]:
        print_slowly("Invalid input. Please enter 'y' or 'n'.\n")
        play_again = input_slowly("Do you want to play again? (y/n): ")
    return play_again.lower() == "y"


def play_game():
    """
    Run a single game of blackjack.
    """
    player_count = get_player_count()
    players = get_player_names(player_count)
    deck = create_deck()
    dealer_name = "Dealer"

    while True:
        if not display_chips(players):
            break

        players = get_bet_and_active_players(players)

        if not players:
            break

        dealer_hand = deal_and_play_turns(players, deck, dealer_name)

        # Evaluate results
        if not evaluate_results_and_ask_continue(players, dealer_hand):
            break

    # Save player data
    player_data = {player["name"]: player["chips"] for player in players}
    save_player_data(player_data)

    print("\n__________________________________________________")
    print_slowly("\nFinal Chip Balances:")
    for player in players:
        print_slowly(player["name"] + " - Chips: \t" + str(player["chips"]))
    print("\n__________________________________________________")
    print_slowly("\nThank you for playing!")
    print("\n__________________________________________________")


if __name__ == "__main__":
    play_game()
