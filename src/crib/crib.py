"""Crib class for managing the dealer's crib."""

from typing import List
from src.card.card import Card


class Crib:
    """Represents the dealer's crib in cribbage.

    The crib receives 2 cards from each player (4 total in 2-player game)
    and is scored by the dealer at the end of the hand.
    """

    def __init__(self):
        """Initialize an empty crib."""
        self.cards: List[Card] = []

    def add_card(self, card: Card) -> None:
        """Add a card to the crib.

        Args:
            card: Card to add to the crib
        """
        self.cards.append(card)

    def add_cards(self, cards: List[Card]) -> None:
        """Add multiple cards to the crib.

        Args:
            cards: List of cards to add
        """
        self.cards.extend(cards)

    def clear(self) -> None:
        """Remove all cards from the crib."""
        self.cards = []

    def size(self) -> int:
        """Get the number of cards in the crib.

        Returns:
            int: Number of cards in crib
        """
        return len(self.cards)

    def is_empty(self) -> bool:
        """Check if the crib is empty.

        Returns:
            bool: True if crib has no cards
        """
        return len(self.cards) == 0

    def get_cards(self) -> List[Card]:
        """Get all cards in the crib.

        Returns:
            List of Card objects
        """
        return self.cards.copy()

    def __len__(self) -> int:
        """Return the number of cards in the crib."""
        return len(self.cards)

    def __str__(self) -> str:
        """String representation of the crib."""
        if not self.cards:
            return "Crib(empty)"
        return "Crib(" + ", ".join(str(card) for card in self.cards) + ")"

    def __repr__(self) -> str:
        """Developer representation of the crib."""
        return f"Crib({len(self.cards)} cards: {[str(c) for c in self.cards]})"
