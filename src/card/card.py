"""Card class for representing individual playing cards in cribbage."""


class Card:
    """Represents a single playing card with rank and suit.

    In cribbage, face cards (J, Q, K) count as 10, and Aces count as 1.
    """

    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    SUITS = ["♠", "♥", "♦", "♣"]

    def __init__(self, rank: str, suit: str):
        """Initialize a card with rank and suit.

        Args:
            rank: Card rank (A, 2-10, J, Q, K)
            suit: Card suit (♠, ♥, ♦, ♣)

        Raises:
            ValueError: If rank or suit is invalid
        """
        if rank not in self.RANKS:
            raise ValueError(f"Invalid rank: {rank}. Must be one of {self.RANKS}")
        if suit not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit}. Must be one of {self.SUITS}")

        self.rank = rank
        self.suit = suit

    @property
    def value(self) -> int:
        """Get the numerical value of the card for counting to 31.

        Returns:
            int: Card value (Ace=1, 2-10=face value, J/Q/K=10)
        """
        if self.rank == "A":
            return 1
        elif self.rank in ["J", "Q", "K"]:
            return 10
        else:
            return int(self.rank)

    @property
    def rank_value(self) -> int:
        """Get the rank value for scoring purposes (A=1, 2=2, ..., K=13).

        Returns:
            int: Rank value from 1-13
        """
        return self.RANKS.index(self.rank) + 1

    def __str__(self) -> str:
        """String representation of the card."""
        return f"{self.rank}{self.suit}"

    def __repr__(self) -> str:
        """Developer representation of the card."""
        return f"Card('{self.rank}', '{self.suit}')"

    def __eq__(self, other) -> bool:
        """Check if two cards are equal (same rank and suit)."""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self) -> int:
        """Make cards hashable for use in sets and dicts."""
        return hash((self.rank, self.suit))
