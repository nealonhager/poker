#!/usr/bin/env python3
"""
Texas Hold'em Best Hand Quiz CLI Program

A multiple choice quiz that tests knowledge of Texas Hold'em hand rankings.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class Suit(Enum):
    """Card suits."""

    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    """Card ranks."""

    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


@dataclass
class Card:
    """Represents a playing card."""

    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        """String representation of the card."""
        rank_str = {
            Rank.TWO: "2",
            Rank.THREE: "3",
            Rank.FOUR: "4",
            Rank.FIVE: "5",
            Rank.SIX: "6",
            Rank.SEVEN: "7",
            Rank.EIGHT: "8",
            Rank.NINE: "9",
            Rank.TEN: "10",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.ACE: "A",
        }[self.rank]
        return f"{rank_str}{self.suit.value}"

    def __eq__(self, other: object) -> bool:
        """Check if two cards are equal."""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self) -> int:
        """Make card hashable."""
        return hash((self.rank, self.suit))

    def is_red(self) -> bool:
        """Check if card is red (hearts or diamonds)."""
        return self.suit in (Suit.HEARTS, Suit.DIAMONDS)


class Hand:
    """Represents a player's hand (2 cards)."""

    def __init__(self, card1: Card, card2: Card):
        """
        Initialize a hand with two cards.

        Args:
            card1: First card in the hand.
            card2: Second card in the hand.
        """
        self.cards = [card1, card2]

    def __str__(self) -> str:
        """String representation of the hand."""
        return f"{self.cards[0]} {self.cards[1]}"

    def get_best_hand(self, board: "Board") -> Tuple[int, List[int], str]:
        """
        Get the best possible hand using this hand and the board.

        Args:
            board: The community board with 5 cards.

        Returns:
            Tuple of (hand_rank, tiebreaker_values, hand_name).
            Lower hand_rank is better (0 = straight flush, 8 = high card).
        """
        all_cards = self.cards + board.cards
        return evaluate_best_hand(all_cards)


class Board:
    """Represents the community board (5 cards)."""

    def __init__(self, cards: List[Card]):
        """
        Initialize board with 5 cards.

        Args:
            cards: List of exactly 5 cards for the community board.

        Raises:
            ValueError: If the number of cards is not exactly 5.
        """
        if len(cards) != 5:
            raise ValueError("Board must have exactly 5 cards")
        self.cards = cards

    def __str__(self) -> str:
        """String representation of the board."""
        return " ".join(str(card) for card in self.cards)


def create_deck() -> List[Card]:
    """
    Create a standard 52-card deck.

    Returns:
        List of 52 Card objects representing a standard deck.
    """
    deck = []
    for suit in Suit:
        for rank in Rank:
            deck.append(Card(rank, suit))
    return deck


def evaluate_best_hand(cards: List[Card]) -> Tuple[int, List[int], str]:
    """
    Evaluate the best 5-card hand from 7 cards.

    Args:
        cards: List of 7 cards (2 hole cards + 5 board cards).

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name).
        Lower hand_rank is better (0 = straight flush, 8 = high card).

    Raises:
        ValueError: If fewer than 5 cards are provided.
    """
    if len(cards) < 5:
        raise ValueError("Need at least 5 cards to evaluate a hand")

    # Generate all possible 5-card combinations
    from itertools import combinations

    best_rank = 8
    best_tiebreakers: List[int] = []
    best_name = "High Card"

    for combo in combinations(cards, 5):
        rank, tiebreakers, name = evaluate_five_card_hand(list(combo))
        if rank < best_rank or (rank == best_rank and tiebreakers > best_tiebreakers):
            best_rank = rank
            best_tiebreakers = tiebreakers
            best_name = name

    return (best_rank, best_tiebreakers, best_name)


def _check_flush(suits: List[Suit]) -> bool:
    """
    Check if all cards have the same suit.

    Args:
        suits: List of card suits.

    Returns:
        True if all cards have the same suit, False otherwise.
    """
    return len(set(suits)) == 1


def _check_straight(ranks: List[int]) -> Tuple[bool, List[int]]:
    """
    Check if ranks form a straight.

    Args:
        ranks: Sorted list of rank values in descending order.

    Returns:
        Tuple of (is_straight, adjusted_ranks). Adjusted ranks handle
        the wheel straight (A-2-3-4-5) where ace is treated as low.
    """
    if len(set(ranks)) != 5:
        return (False, ranks)

    if ranks[0] - ranks[4] == 4:
        return (True, ranks)
    # Check for A-2-3-4-5 straight (wheel)
    if ranks == [14, 5, 4, 3, 2]:
        return (True, [5, 4, 3, 2, 1])  # Treat ace as low for tiebreaker

    return (False, ranks)


def _check_straight_flush(
    ranks: List[int], suits: List[Suit]
) -> Optional[Tuple[int, List[int], str]]:
    """
    Check for straight flush.

    Args:
        ranks: Sorted list of rank values in descending order.
        suits: List of card suits.

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name) if straight flush,
        None otherwise.
    """
    is_flush = _check_flush(suits)
    is_straight, adjusted_ranks = _check_straight(ranks)

    if is_straight and is_flush:
        return (
            0,
            adjusted_ranks,
            f"Straight Flush ({get_rank_name(adjusted_ranks[0])} high)",
        )

    return None


def _check_four_of_a_kind(
    rank_counts: Dict[int, int],
) -> Optional[Tuple[int, List[int], str]]:
    """
    Check for four of a kind.

    Args:
        rank_counts: Dictionary mapping rank values to their counts.

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name) if four of a kind,
        None otherwise.
    """
    counts = sorted(rank_counts.values(), reverse=True)
    if counts != [4, 1]:
        return None

    four_rank = [r for r, c in rank_counts.items() if c == 4][0]
    kicker = [r for r, c in rank_counts.items() if c == 1][0]
    return (1, [four_rank, kicker], f"Four of a Kind ({get_rank_name(four_rank)}s)")


def _check_full_house(
    rank_counts: Dict[int, int],
) -> Optional[Tuple[int, List[int], str]]:
    """
    Check for full house.

    Args:
        rank_counts: Dictionary mapping rank values to their counts.

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name) if full house,
        None otherwise.
    """
    counts = sorted(rank_counts.values(), reverse=True)
    if counts != [3, 2]:
        return None

    three_rank = [r for r, c in rank_counts.items() if c == 3][0]
    pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
    return (
        2,
        [three_rank, pair_rank],
        f"Full House ({get_rank_name(three_rank)}s over {get_rank_name(pair_rank)}s)",
    )


def _check_flush_hand(
    ranks: List[int], suits: List[Suit]
) -> Optional[Tuple[int, List[int], str]]:
    """
    Check for flush (not straight flush).

    Args:
        ranks: Sorted list of rank values in descending order.
        suits: List of card suits.

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name) if flush,
        None otherwise.
    """
    if _check_flush(suits):
        return (3, ranks, f"Flush ({get_rank_name(ranks[0])} high)")
    return None


def _check_straight_hand(ranks: List[int]) -> Optional[Tuple[int, List[int], str]]:
    """
    Check for straight (not straight flush).

    Args:
        ranks: Sorted list of rank values in descending order.

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name) if straight,
        None otherwise.
    """
    is_straight, adjusted_ranks = _check_straight(ranks)
    if is_straight:
        return (
            4,
            adjusted_ranks,
            f"Straight ({get_rank_name(adjusted_ranks[0])} high)",
        )
    return None


def _check_three_of_a_kind(
    rank_counts: Dict[int, int],
) -> Optional[Tuple[int, List[int], str]]:
    """
    Check for three of a kind.

    Args:
        rank_counts: Dictionary mapping rank values to their counts.

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name) if three of a kind,
        None otherwise.
    """
    counts = sorted(rank_counts.values(), reverse=True)
    if counts != [3, 1, 1]:
        return None

    three_rank = [r for r, c in rank_counts.items() if c == 3][0]
    kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
    return (
        5,
        [three_rank] + kickers,
        f"Three of a Kind ({get_rank_name(three_rank)}s)",
    )


def _check_two_pair(
    rank_counts: Dict[int, int],
) -> Optional[Tuple[int, List[int], str]]:
    """
    Check for two pair.

    Args:
        rank_counts: Dictionary mapping rank values to their counts.

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name) if two pair,
        None otherwise.
    """
    counts = sorted(rank_counts.values(), reverse=True)
    if counts != [2, 2, 1]:
        return None

    pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
    kicker = [r for r, c in rank_counts.items() if c == 1][0]
    return (
        6,
        pairs + [kicker],
        f"Two Pair ({get_rank_name(pairs[0])}s and {get_rank_name(pairs[1])}s)",
    )


def _check_one_pair(
    rank_counts: Dict[int, int],
) -> Optional[Tuple[int, List[int], str]]:
    """
    Check for one pair.

    Args:
        rank_counts: Dictionary mapping rank values to their counts.

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name) if one pair,
        None otherwise.
    """
    counts = sorted(rank_counts.values(), reverse=True)
    if counts != [2, 1, 1, 1]:
        return None

    pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
    kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
    return (7, [pair_rank] + kickers, f"Pair of {get_rank_name(pair_rank)}s")


def evaluate_five_card_hand(cards: List[Card]) -> Tuple[int, List[int], str]:
    """
    Evaluate a 5-card hand.

    Args:
        cards: List of exactly 5 cards to evaluate.

    Returns:
        Tuple of (hand_rank, tiebreaker_values, hand_name).
        Lower hand_rank is better (0 = straight flush, 8 = high card).
    """
    ranks = sorted([card.rank.value for card in cards], reverse=True)
    suits = [card.suit for card in cards]

    # Count ranks
    rank_counts: Dict[int, int] = {}
    for rank in ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1

    # Check hand types in order of rank (best to worst)
    result = _check_straight_flush(ranks, suits)
    if result:
        return result

    result = _check_four_of_a_kind(rank_counts)
    if result:
        return result

    result = _check_full_house(rank_counts)
    if result:
        return result

    result = _check_flush_hand(ranks, suits)
    if result:
        return result

    result = _check_straight_hand(ranks)
    if result:
        return result

    result = _check_three_of_a_kind(rank_counts)
    if result:
        return result

    result = _check_two_pair(rank_counts)
    if result:
        return result

    result = _check_one_pair(rank_counts)
    if result:
        return result

    # High card
    return (8, ranks, f"High Card ({get_rank_name(ranks[0])})")


def get_rank_name(rank_value: int) -> str:
    """
    Get the name of a rank value.

    Args:
        rank_value: Integer value of the rank (2-14).

    Returns:
        String name of the rank (e.g., "Two", "Ace"). If rank_value is not
        in the standard range, returns the string representation of the value.
    """
    rank_map = {
        2: "Two",
        3: "Three",
        4: "Four",
        5: "Five",
        6: "Six",
        7: "Seven",
        8: "Eight",
        9: "Nine",
        10: "Ten",
        11: "Jack",
        12: "Queen",
        13: "King",
        14: "Ace",
    }
    return rank_map.get(rank_value, str(rank_value))


def format_card(card: Card) -> str:
    """
    Format a card with color if it's red.

    Args:
        card: The card to format.

    Returns:
        String representation of the card with ANSI color codes for red cards.
    """
    card_str = str(card)
    if card.is_red():
        # ANSI escape code for red text
        return f"\033[91m{card_str}\033[0m"
    return card_str


def format_cards(cards: List[Card]) -> str:
    """
    Format a list of cards with proper coloring.

    Args:
        cards: List of cards to format.

    Returns:
        Space-separated string of formatted cards with color codes.
    """
    return " ".join(format_card(card) for card in cards)


def generate_quiz() -> Tuple[Board, List[Hand], int]:
    """
    Generate a quiz question with board and multiple player hands.

    Returns:
        Tuple of (board, hands, correct_answer_index).
        The correct_answer_index indicates which hand in the list is the best.
    """
    deck = create_deck()
    random.shuffle(deck)

    # Draw 5 cards for the board
    board_cards = deck[:5]
    board = Board(board_cards)
    remaining_deck = deck[5:]

    # Generate 4-9 player hands
    num_hands = random.randint(4, 9)
    hands: List[Hand] = []

    for i in range(num_hands):
        if len(remaining_deck) < 2:
            break
        hand = Hand(remaining_deck[0], remaining_deck[1])
        hands.append(hand)
        remaining_deck = remaining_deck[2:]

    # Evaluate all hands to find the best one
    hand_evaluations = []
    for hand in hands:
        rank, tiebreakers, name = hand.get_best_hand(board)
        hand_evaluations.append((rank, tiebreakers, name, hand))

    # Find the best hand (lowest rank, then highest tiebreakers)
    best_idx = 0
    best_eval = hand_evaluations[0]
    for i, eval_result in enumerate(hand_evaluations[1:], 1):
        rank, tiebreakers, name, hand = eval_result
        best_rank, best_tiebreakers, best_name, best_hand = best_eval

        if rank < best_rank or (rank == best_rank and tiebreakers > best_tiebreakers):
            best_idx = i
            best_eval = eval_result

    return (board, hands, best_idx)


def display_quiz(board: Board, hands: List[Hand], correct_idx: int) -> None:
    """
    Display the quiz question.

    Args:
        board: The community board to display.
        hands: List of player hands to display.
        correct_idx: Index of the correct answer (use -1 to hide the answer).
    """
    print("\n" + "=" * 60)
    print("TEXAS HOLD'EM BEST HAND QUIZ")
    print("=" * 60)
    print("\nBoard (Community Cards):")
    print(format_cards(board.cards))
    print("\nPlayer Hands:")

    labels = "ABCDEFGHI"
    for i, hand in enumerate(hands):
        label = labels[i]
        marker = " ← BEST HAND" if i == correct_idx else ""
        print(f"  {label}) {format_cards(hand.cards)}{marker}")


def main() -> None:
    """Main quiz loop."""
    print("Welcome to Texas Hold'em Best Hand Quiz!")
    print("Type 'quit' to exit at any time.\n")

    score = 0
    total = 0

    while True:
        board, hands, correct_idx = generate_quiz()

        # Don't show the answer initially
        display_quiz(board, hands, -1)

        print("\nWhich hand is the best? (Enter A, B, C, etc.)")
        user_input = input("Your answer: ").strip().upper()

        if user_input == "QUIT":
            break

        if not user_input or user_input not in "ABCDEFGHI":
            print("Invalid input. Please enter A, B, C, etc.")
            continue

        user_choice = ord(user_input) - ord("A")

        if user_choice >= len(hands):
            max_choice = chr(ord("A") + len(hands) - 1)
            print(f"Invalid choice. Please enter A through {max_choice}.")
            continue

        total += 1

        # Show the answer
        print("\n" + "=" * 60)
        display_quiz(board, hands, correct_idx)

        rank, tiebreakers, name = hands[correct_idx].get_best_hand(board)
        print(f"\nBest Hand: {name}")

        if user_choice == correct_idx:
            print("✓ Correct!")
            score += 1
        else:
            print(f"✗ Incorrect. The correct answer was {chr(ord('A') + correct_idx)}.")
            user_rank, user_tiebreakers, user_name = hands[user_choice].get_best_hand(
                board
            )
            print(f"  Your choice ({chr(ord('A') + user_choice)}) has: {user_name}")

        print(f"\nScore: {score}/{total}")
        print("\nPress Enter to continue or type 'quit' to exit...")
        continue_input = input().strip().lower()
        if continue_input == "quit":
            break

    print(f"\nFinal Score: {score}/{total}")
    if total > 0:
        percentage = (score / total) * 100
        print(f"Accuracy: {percentage:.1f}%")
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
