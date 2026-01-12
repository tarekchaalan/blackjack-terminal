"""
ASCII UI helpers for the terminal Blackjack game.

Provides:
- clear_screen: ANSI clear with cursor reset
- render_card: render a single card (or hidden card) to ASCII lines
- render_hand: render multiple cards side-by-side
- render_table: draw the full table with dealer and all players
- show_title: animated title banner
"""

from typing import List, Dict, Optional
from termcolor import colored
import sys
import time
import shutil
import platform


# Card geometry
CARD_WIDTH = 11
CARD_HEIGHT = 7

# Tunable animation timings (seconds)
# Use slightly longer delay for dealer actions so players can follow along
DELAY_DEAL = 0.28
DELAY_REVEAL = 0.55
DELAY_HIT_PLAYER = 0.28
DELAY_HIT_DEALER = 0.65
DELAY_FLASH = 0.9


def interactive_sleep(seconds: float) -> None:
    """Sleep only when running in an interactive terminal (TTY)."""
    try:
        if sys.stdin.isatty():
            time.sleep(seconds)
    except Exception:
        pass


def clear_screen() -> None:
    """Clear terminal screen and move cursor to top-left."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def _color_for_suit(suit: str) -> str:
    return "red" if suit in ("♥", "♦") else "white"


def render_card(card: Optional[str], hidden: bool = False) -> List[str]:
    """
    Render a single card to ASCII lines of fixed size. If hidden, show a pattern back.
    card examples: "A♠", "10♦", "K♥". If card is None, render an empty slot.
    """
    top = "┌" + "─" * (CARD_WIDTH - 2) + "┐"
    bottom = "└" + "─" * (CARD_WIDTH - 2) + "┘"

    if card is None:
        mid = ["│" + " " * (CARD_WIDTH - 2) + "│" for _ in range(CARD_HEIGHT - 2)]
        return [top, *mid, bottom]

    if hidden:
        # Patterned back
        mid = []
        for i in range(CARD_HEIGHT - 2):
            pattern = "░░▒▒" if i % 2 == 0 else "▒▒░░"
            fill = (pattern * ((CARD_WIDTH - 2) // len(pattern) + 1))[: (CARD_WIDTH - 2)]
            mid.append("│" + colored(fill, "blue") + "│")
        return [top, *mid, bottom]

    # Visible card
    rank = card[:-1]
    suit = card[-1]
    rank_left = rank
    rank_right = rank

    # Center the suit while ignoring ANSI escape lengths by computing padding before coloring
    inner_width = CARD_WIDTH - 2
    visible_len = len(suit)
    left_pad = max(0, (inner_width - visible_len) // 2)
    right_pad = max(0, inner_width - visible_len - left_pad)
    suit_line_content = (" " * left_pad) + colored(suit, _color_for_suit(suit)) + (" " * right_pad)

    # Lines
    line1 = f"│{rank_left:<{inner_width}}│"
    line2 = f"│{'':<{inner_width}}│"
    line3 = f"│{suit_line_content}│"
    line4 = f"│{'':<{inner_width}}│"
    line5 = f"│{rank_right:>{inner_width}}│"
    return [top, line1, line2, line3, line4, line5, bottom]


def render_hand(cards: List[str], hide_second: bool = False) -> List[str]:
    """
    Render a set of cards side-by-side. If hide_second is True, hides cards[1] only.
    Returns a list of text lines.
    """
    if not cards:
        return []
    card_lines: List[List[str]] = []
    for idx, c in enumerate(cards):
        hidden = hide_second and idx == 1
        card_lines.append(render_card(c, hidden=hidden))

    # stitch horizontally
    stitched: List[str] = []
    for row in range(CARD_HEIGHT):
        stitched.append(" ".join(lines[row] for lines in card_lines))
    return stitched


def _fit_text(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    return text[: max(0, width - 1)] + "…"


def show_title() -> None:
    cols = shutil.get_terminal_size((100, 30)).columns
    banner = [
        "██████╗ ██╗      █████╗  ██████╗██╗  ██╗     ██╗ █████╗  ██████╗██╗  ██╗",
        "██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝     ██║██╔══██╗██╔════╝██║ ██╔╝",
        "██████╔╝██║     ███████║██║     █████╔╝      ██║███████║██║     █████╔╝ ",
        "██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██   ██║██╔══██║██║     ██╔═██╗ ",
        "███████║███████╗██║  ██║╚██████╗██║  ██╗╚█████╔╝██║  ██║╚██████╗██║  ██╗",
        "╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝",
    ]

    clear_screen()
    for line in banner:
        padding = max(0, (cols - len(line)) // 2)
        print(" " * padding + colored(line, "green", attrs=["bold"]))
        interactive_sleep(0.03)
    subtitle = "Interactive ASCII Blackjack"
    pad = max(0, (cols - len(subtitle)) // 2)
    print("\n" + " " * pad + colored(subtitle, "cyan"))
    interactive_sleep(0.4)


def render_table(
    players: List[Dict],
    dealer: Optional[Dict],
    *,
    hide_dealer_hole: bool = True,
    focus_player_index: Optional[int] = None,
    message: Optional[str] = None,
    show_hint: bool = True,
) -> None:
    """
    Draw the full table view. players/dealer contain fields like name, hand, chips, bet, cardvalue, status.
    """
    cols = shutil.get_terminal_size((100, 30)).columns
    clear_screen()

    # Dealer area
    title = "Dealer"
    print(colored(title, "red", attrs=["bold"]))
    if dealer and dealer.get("hand"):
        hand_lines = render_hand(dealer["hand"], hide_second=hide_dealer_hole)
        for line in hand_lines:
            print(line)
        if not hide_dealer_hole:
            val = dealer.get("cardvalue")
            if val is not None:
                print(colored(f"Value: {val}", "cyan"))
    else:
        print("(no cards)\n")

    print("\n" + "═" * min(cols, 120))

    # Players grid (one by one vertically)
    for idx, p in enumerate(players):
        name = p.get("name", f"Player {idx+1}")
        chips = p.get("chips", 0)
        bet = p.get("bet", 0)
        val = p.get("cardvalue")
        status = p.get("status")
        header = f"{name}  |  Chips: {chips}  Bet: {bet}"
        is_focus = idx == focus_player_index
        header_color = ("green" if is_focus else "white")
        print(colored(_fit_text(header, cols), header_color, attrs=["bold"]))
        if p.get("hand"):
            lines = render_hand(p["hand"], hide_second=False)
            for line in lines:
                print(line)
        if val is not None:
            print(colored(f"Value: {val}", "cyan"), end="")
            if status:
                print("  " + colored(f"{status.upper()}", "yellow", attrs=["bold"]))
            else:
                print()
        print()

    if message:
        print(colored(_fit_text(message, cols), "magenta"))

    # Small instruction hint
    if show_hint:
        print(colored("(H)it  (S)tand  (D)ouble", "white"))


def flash_message(text: str, duration: float = 0.8) -> None:
    """Quick centered message flash."""
    cols = shutil.get_terminal_size((100, 30)).columns
    pad = max(0, (cols - len(text)) // 2)
    print("\n" + " " * pad + colored(text, "yellow", attrs=["bold"]))
    time.sleep(duration)


def deal_animation(
    players: List[Dict], dealer: Dict, *, hide_dealer_hole: bool = True, delay: Optional[float] = None
) -> None:
    """Simple re-render loop to simulate dealing; call after each card change."""
    render_table(players, dealer, hide_dealer_hole=hide_dealer_hole)
    # Choose default delay if not provided
    if delay is None:
        delay = DELAY_DEAL if hide_dealer_hole else DELAY_HIT_PLAYER
    interactive_sleep(delay)


