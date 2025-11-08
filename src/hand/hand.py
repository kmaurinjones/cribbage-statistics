"""Hand class for managing a player's cards."""

from typing import List
from src.card.card import Card


class Hand:
    """Represents a player's hand of cards.

    In cribbage, players are dealt 6 cards and must discard 2 to the crib,
    leaving 4 cards for play.
    """

    def __init__(self, cards: List[Card] = None):
        """Initialize a hand with optional starting cards.

        Args:
            cards: Optional list of Card objects to initialize the hand
        """
        self.cards: List[Card] = cards if cards is not None else []

    def add_card(self, card: Card) -> None:
        """Add a card to the hand.

        Args:
            card: Card to add to the hand
        """
        self.cards.append(card)

    def add_cards(self, cards: List[Card]) -> None:
        """Add multiple cards to the hand.

        Args:
            cards: List of cards to add
        """
        self.cards.extend(cards)

    def remove_card(self, card: Card) -> Card:
        """Remove a specific card from the hand.

        Args:
            card: Card to remove

        Returns:
            The removed card

        Raises:
            ValueError: If card is not in hand
        """
        if card not in self.cards:
            raise ValueError(f"Card {card} not in hand")
        self.cards.remove(card)
        return card

    def remove_cards(self, cards: List[Card]) -> List[Card]:
        """Remove multiple specific cards from the hand.

        Args:
            cards: List of cards to remove

        Returns:
            List of removed cards

        Raises:
            ValueError: If any card is not in hand
        """
        for card in cards:
            if card not in self.cards:
                raise ValueError(f"Card {card} not in hand")

        for card in cards:
            self.cards.remove(card)

        return cards

    def clear(self) -> None:
        """Remove all cards from the hand."""
        self.cards = []

    def size(self) -> int:
        """Get the number of cards in the hand.

        Returns:
            int: Number of cards in hand
        """
        return len(self.cards)

    def is_empty(self) -> bool:
        """Check if the hand is empty.

        Returns:
            bool: True if hand has no cards
        """
        return len(self.cards) == 0

    def get_cards(self) -> List[Card]:
        """Get all cards in the hand.

        Returns:
            List of Card objects
        """
        return self.cards.copy()

    def __len__(self) -> int:
        """Return the number of cards in the hand."""
        return len(self.cards)

    def __str__(self) -> str:
        """String representation of the hand."""
        if not self.cards:
            return "Hand(empty)"
        return "Hand(" + ", ".join(str(card) for card in self.cards) + ")"

    def __repr__(self) -> str:
        """Developer representation of the hand."""
        return f"Hand({len(self.cards)} cards: {[str(c) for c in self.cards]})"
