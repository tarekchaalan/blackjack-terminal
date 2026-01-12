#! /usr/bin/env python3

# Tarek Chaalan
# @tarekchaalan

"""
This is a text-based blackjack game, played in the terminal.
"""

from termcolor import colored
import json
import sys
import time
import platform
import os
if platform.system() != 'Windows':
    import termios
    import tty
else:
    try:
        import colorama
        colorama.init()
    except Exception:
        pass

from game import (
    deal_initial_cards,
    play_player_turn,
    play_dealer_turn,
    evaluate_hand,
)
from deck import create_deck
from card import get_count_value
from ui import (
    show_title,
    render_table,
    deal_animation,
    flash_message,
    DELAY_HIT_DEALER,
    DELAY_REVEAL,
)
_autoplay_bet_index = 0

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

    # Autoplay responses for non-interactive runs
    if os.environ.get("BJ_AUTOPLAY") == "1":
        lower = prompt.lower()
        if "number of players" in lower:
            return "1"
        if "enter player" in lower and "name" in lower:
            return "Bot"
        if "bet amount" in lower:
            return "10"
        if "choose an action" in lower:
            return "s"
        if "play again" in lower:
            return "n"
        if "would you like to accept?" in lower:
            return "y"
        if "running count" in lower:
            return "n"
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
        json.dump(data, file, ensure_ascii=False, indent=2)


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
                topup = input_slowly(
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
    autoplay = os.environ.get("BJ_AUTOPLAY") == "1"
    names_env = os.environ.get("BJ_NAMES", "").split(",") if autoplay else []
    for i in range(player_count):
        if autoplay and i < len(names_env) and names_env[i].strip():
            player_name = names_env[i].strip()
        else:
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
    global _autoplay_bet_index
    autoplay = os.environ.get("BJ_AUTOPLAY") == "1"
    bets_env = os.environ.get("BJ_BETS", "").split(",") if autoplay else []
    while True:
        if player["chips"] == 0:
            return 0
        try:
            if autoplay:
                # Use per-player bet if provided, else BJ_BET or default 10
                bet_str = None
                if _autoplay_bet_index < len(bets_env) and bets_env[_autoplay_bet_index].strip():
                    bet_str = bets_env[_autoplay_bet_index].strip()
                bet = float(bet_str or os.environ.get("BJ_BET", "10"))
                _autoplay_bet_index += 1
            else:
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
    autoplay = os.environ.get("BJ_AUTOPLAY") == "1"
    if autoplay:
        try:
            return max(1, int(os.environ.get("BJ_PLAYERS", "1")))
        except ValueError:
            return 1
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


def deal_and_play_turns(players, deck, dealer_name, running_count):
    """
    Deal the initial cards and play the player and dealer turns.
    Returns (dealer_hand, new_running_count).
    """
    print_slowly("\n")
    reshuffled = False

    # Reset transient round state
    for p in players:
        if "status" in p:
            p.pop("status", None)

    # Initial deal with animations and table updates
    for player in players:
        player, player_reshuffled = deal_initial_cards(player, deck)
        if player_reshuffled:
            reshuffled = True
        render_table(players, None, hide_dealer_hole=True)
        deal_animation(players, {"name": dealer_name, "hand": []}, hide_dealer_hole=True)

    dealer_hand, dealer_reshuffled = deal_initial_cards({"name": dealer_name}, deck, True)
    if dealer_reshuffled:
        reshuffled = True
    render_table(players, dealer_hand, hide_dealer_hole=True)
    deal_animation(players, dealer_hand, hide_dealer_hole=True)

    # If reshuffled during initial deal, notify and reset count
    if reshuffled:
        flash_message("🔄 NEW SHOE SHUFFLED - Count reset to 0")
        running_count = 0

    def on_reshuffle():
        nonlocal running_count, reshuffled
        flash_message("🔄 NEW SHOE SHUFFLED - Count reset to 0")
        running_count = 0
        reshuffled = True

    # Player turns
    for idx, player in enumerate(players):
        while True:
            render_table(players, dealer_hand, hide_dealer_hole=True, focus_player_index=idx, message=f"{player['name']}'s turn")
            if player.get("status") in {"blackjack", "bust"}:
                break
            play_player_turn(
                player,
                deck,
                on_update=lambda: render_table(players, dealer_hand, hide_dealer_hole=True, focus_player_index=idx),
                on_reshuffle=on_reshuffle
            )
            render_table(players, dealer_hand, hide_dealer_hole=True, focus_player_index=idx)
            if player.get("status") in {"blackjack", "bust", "stand", "double"}:
                break

    # Dealer's turn: step-by-step with clear prompts
    # 1) Show with hole hidden
    render_table(
        players,
        dealer_hand,
        hide_dealer_hole=True,
        message="Dealer is about to reveal their hole card...",
    )
    deal_animation(players, dealer_hand, hide_dealer_hole=True, delay=DELAY_REVEAL)
    # 2) Reveal hole card
    render_table(
        players,
        dealer_hand,
        hide_dealer_hole=False,
        message="Dealer reveals the hole card",
    )
    deal_animation(players, dealer_hand, hide_dealer_hole=False, delay=DELAY_REVEAL)
    # 3) Play dealer hits with live updates and slower pacing
    play_dealer_turn(
        dealer_hand,
        deck,
        on_update=lambda: deal_animation(
            players,
            dealer_hand,
            hide_dealer_hole=False,
            delay=DELAY_HIT_DEALER,
        ),
        on_reshuffle=on_reshuffle
    )
    render_table(players, dealer_hand, hide_dealer_hole=False)
    return dealer_hand, running_count


def update_running_count(players, dealer_hand, running_count):
    """
    Update the running count based on all cards dealt this round.
    """
    count_change = 0

    # Count all player cards
    for player in players:
        for card in player["hand"]:
            count_change += get_count_value(card)

    # Count dealer cards
    for card in dealer_hand["hand"]:
        count_change += get_count_value(card)

    return running_count + count_change

def evaluate_results_and_ask_continue(players, dealer_hand, running_count):
    """
    Evaluate the results and ask the user if they want to continue.
    """
    for player in players:
        evaluate_hand(player, dealer_hand)
    render_table(players, dealer_hand, hide_dealer_hole=False, show_hint=False)

    # Update the running count with this round's cards
    new_count = update_running_count(players, dealer_hand, running_count)

    # Ask if they want to see the count
    show_count = input_slowly("\nWould you like to see the running count? (y/n): ")
    while show_count.lower() not in ["y", "n"]:
        print_slowly("Invalid input. Please enter 'y' or 'n'.\n")
        show_count = input_slowly("Would you like to see the running count? (y/n): ")

    if show_count.lower() == "y":
        print_slowly(f"\nRunning Count: {new_count}")

    play_again = input_slowly("\nDo you want to play again? (y/n): ")
    while play_again.lower() not in ["y", "n"]:
        print_slowly("Invalid input. Please enter 'y' or 'n'.\n")
        play_again = input_slowly("Do you want to play again? (y/n): ")
    return play_again.lower() == "y", new_count


def play_game():
    """
    Run a single game of blackjack.
    """
    show_title()
    player_count = get_player_count()
    players = get_player_names(player_count)
    deck = create_deck()
    dealer_name = "Dealer"
    running_count = 0  # Initialize card counting

    while True:
        if not display_chips(players):
            break

        players = get_bet_and_active_players(players)

        if not players:
            break

        dealer_hand, running_count = deal_and_play_turns(players, deck, dealer_name, running_count)

        # Evaluate results and update count
        continue_playing, running_count = evaluate_results_and_ask_continue(players, dealer_hand, running_count)
        if not continue_playing:
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
