"""
This file contains the functions that run the game.
"""
from card import get_card_value
from deck import draw_card


def deal_initial_cards(player, deck, is_dealer=False):
    """
    This function deals the initial cards to the player.
    """
    card1 = draw_card(deck)
    card2 = draw_card(deck)
    player["hand"] = [card1, card2]
    player["cardvalue"] = get_hand_value(player["hand"])

    if not is_dealer:
        print(
            player["name"]
            + " has "
            + card1
            + " and "
            + card2
            + " ("
            + str(player["cardvalue"])
            + ")"
        )
    else:
        print("\nDealer has " + card1 + " and an unknown card")

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
            print("Blackjack!")
            break
        if player["cardvalue"] > 21:
            print("Bust!")
            break

        action = input("Choose an action: (H)it, (S)tand, or (D)ouble: ")
        player["doubled"] = False

        if action.lower() == "h":
            card = draw_card(deck)
            player["hand"].append(card)
            player["cardvalue"] = get_hand_value(player["hand"])
            print(
                player["name"]
                + " hits and receives "
                + card
                + " ("
                + str(player["cardvalue"])
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
                print(
                    player["name"]
                    + " Doubles and receives "
                    + card
                    + ". Bet is now "
                    + str(player["bet"])
                    + " ("
                    + str(player["cardvalue"])
                    + ")"
                )
                break
            print("Not enough chips to double. Please choose another action.")
        elif action.lower() == "s":
            break
        else:
            print("Invalid action. Please try again.")


def play_dealer_turn(dealer_hand, deck):
    """
    This function runs the dealer's turn.
    """
    # Reveal the second card
    dealer_card_values = [
        get_card_value(card, dealer_hand["cardvalue"]) for card in dealer_hand["hand"]
    ]
    print(
        "Dealer reveals his second card: "
        + dealer_hand["hand"][1]
        + " ("
        + str(sum(dealer_card_values))
        + ")"
    )

    while True:
        if dealer_hand["cardvalue"] >= 17 and dealer_hand["cardvalue"] <= 21:
            print(dealer_hand["name"] + " stands")
            break
        if dealer_hand["cardvalue"] > 21:
            print(dealer_hand["name"] + " busts")
            break
        card = draw_card(deck)
        dealer_hand["hand"].append(card)
        dealer_hand["cardvalue"] = get_hand_value(dealer_hand["hand"])
        print(
            dealer_hand["name"]
            + " hits and receives "
            + card
            + " ("
            + str(dealer_hand["cardvalue"])
            + ")"
        )


def evaluate_hand(player, dealer_hand):
    """
    This function evaluates the player and dealer's hands.
    """
    print(
        player["name"]
        + "'s Hand: "
        + str(player["hand"])
        + "  ("
        + str(player["cardvalue"])
        + ")"
    )

    if player["cardvalue"] > 21:
        print("Bust!\n")
    elif player["cardvalue"] == dealer_hand["cardvalue"]:
        print("Push!\n")
        player["chips"] += player["bet"]
    elif player["cardvalue"] == 21 and len(player["hand"]) == 2:
        print("Blackjack!\n")
        player["chips"] += player["bet"] * 2
    elif player["cardvalue"] > dealer_hand["cardvalue"] and player["doubled"]:
        print("Won with a Double!\n")
        player["chips"] += player["bet"] * 2  # Double the winnings if player doubled
    elif (
        player["cardvalue"] > dealer_hand["cardvalue"] or dealer_hand["cardvalue"] > 21
    ):
        print("Win!\n")
        player["chips"] += player["bet"] * 2
    elif player["cardvalue"] < dealer_hand["cardvalue"]:
        print("Lose!\n")
