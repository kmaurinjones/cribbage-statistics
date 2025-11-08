"""Player class for cribbage game simulation."""

import numpy as np
from typing import List, Optional
from src.card.card import Card
from src.hand.hand import Hand
from src.rules.rules import Rules


class Player:
    """Represents a player in a cribbage game.

    Handles:
    - Card management (hand)
    - Score tracking
    - Discard decisions
    - Play decisions
    """

    def __init__(self, name: str, random_state: Optional[np.random.RandomState] = None):
        """Initialize a player.

        Args:
            name: Player's name/identifier
            random_state: Optional numpy RandomState for reproducible decisions
        """
        self.name = name
        self.hand = Hand()
        self.play_hand: List[Card] = []  # 4 cards kept for counting after discard
        self.score = 0
        self.play_points = 0  # Points scored during play phase
        self.count_points = 0  # Points scored during count phase
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )

    def add_cards_to_hand(self, cards: List[Card]) -> None:
        """Add cards to the player's hand.

        Args:
            cards: List of cards to add
        """
        self.hand.add_cards(cards)

    def choose_discards(self, is_dealer: bool) -> List[Card]:
        """Choose which cards to discard to the crib.

        Currently uses a simple random strategy.
        TODO: Implement strategic discard logic.

        Args:
            is_dealer: Whether this player is the dealer

        Returns:
            List of 2 cards to discard
        """
        if self.hand.size() != Rules.INITIAL_HAND_SIZE:
            raise ValueError(f"Cannot discard from hand of size {self.hand.size()}")

        # Simple strategy: randomly choose 2 cards to discard
        cards = self.hand.get_cards()
        discard_indices = self.random_state.choice(len(cards), size=2, replace=False)
        discards = [cards[i] for i in discard_indices]

        return discards

    def discard_to_crib(self, cards: List[Card]) -> None:
        """Remove discarded cards from hand and save play hand.

        Args:
            cards: Cards to remove from hand
        """
        self.hand.remove_cards(cards)
        # Save the 4-card play hand for counting phase
        self.play_hand = self.hand.get_cards()

    def choose_play_card(self, current_count: int) -> Optional[Card]:
        """Choose a card to play during the play phase.

        Currently uses a simple strategy: play first legal card.
        TODO: Implement strategic play logic.

        Args:
            current_count: Current count in the play

        Returns:
            Card to play, or None if no legal play
        """
        cards = self.hand.get_cards()

        # Find all playable cards
        playable = [card for card in cards if Rules.can_play_card(card, current_count)]

        if not playable:
            return None

        # Simple strategy: play first playable card
        return playable[0]

    def play_card(self, card: Card) -> Card:
        """Play a card from hand.

        Args:
            card: Card to play

        Returns:
            The played card

        Raises:
            ValueError: If card not in hand
        """
        return self.hand.remove_card(card)

    def add_score(self, points: int, from_play: bool = True) -> None:
        """Add points to player's score.

        Args:
            points: Points to add
            from_play: Whether points are from play phase (True) or count phase (False)
        """
        self.score += points
        if from_play:
            self.play_points += points
        else:
            self.count_points += points

    def get_score(self) -> int:
        """Get player's current score.

        Returns:
            Current score
        """
        return self.score

    def has_cards(self) -> bool:
        """Check if player has cards in hand.

        Returns:
            bool: True if hand is not empty
        """
        return not self.hand.is_empty()

    def clear_hand(self) -> None:
        """Remove all cards from hand."""
        self.hand.clear()
        self.play_hand = []

    def reset_stats(self) -> None:
        """Reset all player statistics for a new game."""
        self.score = 0
        self.play_points = 0
        self.count_points = 0
        self.clear_hand()

    def get_play_points(self) -> int:
        """Get points scored during play phase.

        Returns:
            Total play phase points
        """
        return self.play_points

    def get_count_points(self) -> int:
        """Get points scored during count phase.

        Returns:
            Total count phase points
        """
        return self.count_points

    def get_hand_cards(self) -> List[Card]:
        """Get all cards in player's hand.

        Returns:
            List of Card objects
        """
        return self.hand.get_cards()

    def get_play_hand(self) -> List[Card]:
        """Get the 4-card play hand (for counting phase).

        Returns:
            List of 4 Card objects kept after discarding
        """
        return self.play_hand

    def __str__(self) -> str:
        """String representation of player."""
        return f"{self.name} (Score: {self.score})"

    def __repr__(self) -> str:
        """Developer representation of player."""
        return f"Player(name='{self.name}', score={self.score}, hand_size={self.hand.size()})"
