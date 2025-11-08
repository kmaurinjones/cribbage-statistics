"""Scorer class for calculating cribbage points in all scenarios."""

from typing import List, Tuple, Dict
from itertools import combinations
from src.card.card import Card


class Scorer:
    """Handles all scoring calculations for cribbage.

    Includes scoring for:
    - Play phase (pegging): 15s, pairs, runs, go, 31
    - Count phase (hand/crib): 15s, pairs, runs, flush, nobs
    """

    @staticmethod
    def score_play(
        cards_played: List[Card], last_player_idx: int
    ) -> Tuple[int, List[str]]:
        """Score points during the play phase (pegging).

        Args:
            cards_played: List of cards played in sequence
            last_player_idx: Index of player who played last card

        Returns:
            Tuple of (points scored, list of scoring reasons)
        """
        if not cards_played:
            return 0, []

        points = 0
        reasons = []

        # Calculate current count
        count = sum(card.value for card in cards_played)

        # Check for 15
        if count == 15:
            points += 2
            reasons.append("15 for 2")

        # Check for 31
        if count == 31:
            points += 2
            reasons.append("31 for 2")

        # Check for pairs/triples/quadruples (most recent cards)
        pair_points, pair_reason = Scorer._score_play_pairs(cards_played)
        if pair_points > 0:
            points += pair_points
            reasons.append(pair_reason)

        # Check for runs (sequences of 3+ cards in any order)
        run_points, run_reason = Scorer._score_play_run(cards_played)
        if run_points > 0:
            points += run_points
            reasons.append(run_reason)

        return points, reasons

    @staticmethod
    def _score_play_pairs(cards_played: List[Card]) -> Tuple[int, str]:
        """Score pairs during play phase.

        Args:
            cards_played: List of cards played in sequence

        Returns:
            Tuple of (points, reason string)
        """
        if len(cards_played) < 2:
            return 0, ""

        # Check most recent cards for pairs
        last_rank = cards_played[-1].rank
        pair_count = 1

        for i in range(len(cards_played) - 2, -1, -1):
            if cards_played[i].rank == last_rank:
                pair_count += 1
            else:
                break

        if pair_count == 2:
            return 2, "pair for 2"
        elif pair_count == 3:
            return 6, "triple for 6"
        elif pair_count == 4:
            return 12, "quadruple for 12"

        return 0, ""

    @staticmethod
    def _score_play_run(cards_played: List[Card]) -> Tuple[int, str]:
        """Score runs during play phase.

        A run is 3+ consecutive cards in any order.

        Args:
            cards_played: List of cards played in sequence

        Returns:
            Tuple of (points, reason string)
        """
        if len(cards_played) < 3:
            return 0, ""

        # Try runs of decreasing length starting from all cards
        for run_length in range(len(cards_played), 2, -1):
            recent_cards = cards_played[-run_length:]
            rank_values = sorted([card.rank_value for card in recent_cards])

            # Check if consecutive
            is_run = True
            for i in range(len(rank_values) - 1):
                if rank_values[i + 1] - rank_values[i] != 1:
                    is_run = False
                    break

            if is_run:
                return run_length, f"run of {run_length} for {run_length}"

        return 0, ""

    @staticmethod
    def score_hand(
        hand_cards: List[Card], starter: Card, is_crib: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """Score a hand or crib with the starter card.

        Args:
            hand_cards: List of 4 cards in hand/crib
            starter: The starter (cut) card
            is_crib: Whether this is the crib (affects flush scoring)

        Returns:
            Tuple of (total points, dict of scoring breakdown)
        """
        all_cards = hand_cards + [starter]
        breakdown = {"fifteens": 0, "pairs": 0, "runs": 0, "flush": 0, "nobs": 0}

        # Score 15s
        breakdown["fifteens"] = Scorer._score_fifteens(all_cards)

        # Score pairs
        breakdown["pairs"] = Scorer._score_pairs(all_cards)

        # Score runs
        breakdown["runs"] = Scorer._score_runs(all_cards)

        # Score flush
        breakdown["flush"] = Scorer._score_flush(hand_cards, starter, is_crib)

        # Score nobs (Jack of same suit as starter)
        breakdown["nobs"] = Scorer._score_nobs(hand_cards, starter)

        total = sum(breakdown.values())
        return total, breakdown

    @staticmethod
    def _score_fifteens(cards: List[Card]) -> int:
        """Count all combinations that sum to 15.

        Args:
            cards: List of cards to check

        Returns:
            Points scored (2 per fifteen)
        """
        count = 0
        # Check all possible combinations of cards
        for r in range(1, len(cards) + 1):
            for combo in combinations(cards, r):
                if sum(card.value for card in combo) == 15:
                    count += 1

        return count * 2

    @staticmethod
    def _score_pairs(cards: List[Card]) -> int:
        """Count all pairs in the cards.

        Args:
            cards: List of cards to check

        Returns:
            Points scored (2 per pair)
        """
        count = 0
        for i, card1 in enumerate(cards):
            for card2 in cards[i + 1 :]:
                if card1.rank == card2.rank:
                    count += 1

        return count * 2

    @staticmethod
    def _score_runs(cards: List[Card]) -> int:
        """Find the longest run(s) and score them.

        A run is 3+ consecutive cards. Multiple runs of the same length
        count separately (e.g., double run of 3).

        Args:
            cards: List of cards to check

        Returns:
            Points scored (1 per card per run)
        """
        # Try to find runs from longest to shortest
        for run_length in range(len(cards), 2, -1):
            run_count = 0
            for combo in combinations(cards, run_length):
                rank_values = sorted([card.rank_value for card in combo])

                # Check if consecutive
                is_run = True
                for i in range(len(rank_values) - 1):
                    if rank_values[i + 1] - rank_values[i] != 1:
                        is_run = False
                        break

                if is_run:
                    run_count += 1

            # If we found run(s) of this length, return the score
            if run_count > 0:
                return run_length * run_count

        return 0

    @staticmethod
    def _score_flush(hand_cards: List[Card], starter: Card, is_crib: bool) -> int:
        """Score flush points.

        Args:
            hand_cards: The 4 cards in hand
            starter: The starter card
            is_crib: Whether scoring the crib

        Returns:
            Points scored (4 for hand flush, 5 if starter matches, 0 for crib unless all 5 match)
        """
        if len(hand_cards) != 4:
            return 0

        hand_suit = hand_cards[0].suit
        all_hand_same = all(card.suit == hand_suit for card in hand_cards)

        if not all_hand_same:
            return 0

        # For crib, all 5 cards must match
        if is_crib:
            if starter.suit == hand_suit:
                return 5
            else:
                return 0

        # For hand, 4 cards = 4 points, 5 cards = 5 points
        if starter.suit == hand_suit:
            return 5
        else:
            return 4

    @staticmethod
    def _score_nobs(hand_cards: List[Card], starter: Card) -> int:
        """Score nobs (Jack of same suit as starter).

        Args:
            hand_cards: The 4 cards in hand
            starter: The starter card

        Returns:
            1 if hand contains Jack of starter's suit, else 0
        """
        for card in hand_cards:
            if card.rank == "J" and card.suit == starter.suit:
                return 1
        return 0
