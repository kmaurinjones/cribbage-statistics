"""Rules class for cribbage game constraints and validation."""

from typing import List
from src.card.card import Card


class Rules:
    """Enforces cribbage game rules and constraints.

    Standard two-player cribbage rules:
    - Game to 121 points
    - Each player dealt 6 cards, discards 2 to crib
    - Play to 31 or until no one can play (go)
    - Non-dealer plays first
    - Dealer gets crib
    """

    # Game constants
    WINNING_SCORE = 121
    INITIAL_HAND_SIZE = 6
    CARDS_TO_DISCARD = 2
    PLAY_HAND_SIZE = 4
    MAX_PLAY_COUNT = 31

    @staticmethod
    def is_game_won(score: int) -> bool:
        """Check if a score has reached the winning threshold.

        Args:
            score: Player's current score

        Returns:
            bool: True if score >= 121
        """
        return score >= Rules.WINNING_SCORE

    @staticmethod
    def can_play_card(card: Card, current_count: int) -> bool:
        """Check if a card can be legally played.

        Args:
            card: Card to check
            current_count: Current count in the play

        Returns:
            bool: True if playing the card wouldn't exceed 31
        """
        return current_count + card.value <= Rules.MAX_PLAY_COUNT

    @staticmethod
    def has_playable_card(cards: List[Card], current_count: int) -> bool:
        """Check if any card in the list can be legally played.

        Args:
            cards: List of cards to check
            current_count: Current count in the play

        Returns:
            bool: True if at least one card can be played
        """
        return any(Rules.can_play_card(card, current_count) for card in cards)

    @staticmethod
    def validate_hand_size(hand_size: int, expected_size: int) -> bool:
        """Validate that a hand has the expected number of cards.

        Args:
            hand_size: Actual number of cards
            expected_size: Expected number of cards

        Returns:
            bool: True if sizes match
        """
        return hand_size == expected_size

    @staticmethod
    def validate_discard(hand_size: int, discard_size: int) -> bool:
        """Validate that the discard is legal.

        Args:
            hand_size: Number of cards in hand
            discard_size: Number of cards being discarded

        Returns:
            bool: True if discard is valid
        """
        return (
            hand_size == Rules.INITIAL_HAND_SIZE
            and discard_size == Rules.CARDS_TO_DISCARD
        )

    @staticmethod
    def get_go_points(is_last_player: bool, count: int) -> int:
        """Calculate points for a "go" situation.

        Args:
            is_last_player: Whether this player played the last card
            count: Current count

        Returns:
            Points awarded (1 for go, 2 for 31)
        """
        if count == 31:
            return 2
        elif is_last_player:
            return 1
        return 0

    @staticmethod
    def is_valid_starter(starter: Card, dealt_cards: List[Card]) -> bool:
        """Validate that the starter card wasn't already dealt.

        Args:
            starter: The starter card
            dealt_cards: All cards already dealt to players

        Returns:
            bool: True if starter is valid
        """
        return starter not in dealt_cards

    @staticmethod
    def check_his_heels(starter: Card) -> bool:
        """Check if starter is a Jack (his heels - dealer gets 2 points).

        Args:
            starter: The starter card

        Returns:
            bool: True if starter is a Jack
        """
        return starter.rank == "J"
