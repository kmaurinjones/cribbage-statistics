"""Deck class for managing a standard 52-card deck."""

import numpy as np
from typing import List, Optional
from src.card.card import Card


class Deck:
    """Represents a standard 52-card deck for cribbage.

    Handles shuffling and dealing cards with support for numpy random states
    for reproducibility.
    """

    def __init__(self, random_state: Optional[np.random.RandomState] = None):
        """Initialize a standard 52-card deck.

        Args:
            random_state: Optional numpy RandomState for reproducible shuffling
        """
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )
        self.cards: List[Card] = []
        self.dealt_cards: List[Card] = []
        self._create_deck()

    def _create_deck(self) -> None:
        """Create a fresh 52-card deck."""
        self.cards = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.cards.append(Card(rank, suit))
        self.dealt_cards = []

    def shuffle(self) -> None:
        """Shuffle the deck using the random state."""
        self.random_state.shuffle(self.cards)

    def deal(self, n: int = 1) -> List[Card]:
        """Deal n cards from the top of the deck.

        Args:
            n: Number of cards to deal (default 1)

        Returns:
            List of dealt cards

        Raises:
            ValueError: If not enough cards remain in deck
        """
        if n > len(self.cards):
            raise ValueError(
                f"Cannot deal {n} cards. Only {len(self.cards)} cards remain."
            )

        dealt = self.cards[:n]
        self.cards = self.cards[n:]
        self.dealt_cards.extend(dealt)
        return dealt

    def deal_one(self) -> Card:
        """Deal a single card from the deck.

        Returns:
            Single Card object

        Raises:
            ValueError: If no cards remain in deck
        """
        return self.deal(1)[0]

    def reset(self) -> None:
        """Reset the deck to a fresh, unshuffled state."""
        self._create_deck()

    def cards_remaining(self) -> int:
        """Get the number of cards remaining in the deck.

        Returns:
            int: Number of undealt cards
        """
        return len(self.cards)

    def __len__(self) -> int:
        """Return the number of cards remaining in the deck."""
        return len(self.cards)

    def __repr__(self) -> str:
        """Developer representation of the deck."""
        return f"Deck({len(self.cards)} cards remaining)"
