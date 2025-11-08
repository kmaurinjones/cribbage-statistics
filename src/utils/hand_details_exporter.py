"""Hand-level details CSV exporter for granular analysis."""

import csv
from pathlib import Path
from typing import Dict


class HandDetailsExporter:
    """Exports detailed hand-level information to CSV.

    Tracks every hand played with:
    - Cards dealt, kept, discarded
    - Starter card
    - Hand and crib scores with breakdowns
    - Context (dealer, hand number, game state)
    """

    # CSV field names for hand details
    FIELDNAMES = [
        "game_number",
        "hand_number",
        "dealer",
        # Player 1 details
        "p1_dealt_cards",
        "p1_kept_cards",
        "p1_discards",
        "p1_hand_score",
        "p1_hand_fifteens",
        "p1_hand_pairs",
        "p1_hand_runs",
        "p1_hand_flush",
        "p1_hand_nobs",
        "p1_score_before",
        "p1_score_after",
        # Player 2 details
        "p2_dealt_cards",
        "p2_kept_cards",
        "p2_discards",
        "p2_hand_score",
        "p2_hand_fifteens",
        "p2_hand_pairs",
        "p2_hand_runs",
        "p2_hand_flush",
        "p2_hand_nobs",
        "p2_score_before",
        "p2_score_after",
        # Crib details
        "crib_cards",
        "crib_score",
        "crib_fifteens",
        "crib_pairs",
        "crib_runs",
        "crib_flush",
        "crib_nobs",
        # Shared
        "starter_card",
        "his_heels",
    ]

    def __init__(self, csv_file_path: Path):
        """Initialize hand details exporter.

        Args:
            csv_file_path: Path to CSV file
        """
        self.csv_file_path = csv_file_path

    def write_record(self, record: Dict) -> None:
        """Write a single hand record immediately to CSV.

        Args:
            record: Dictionary containing hand details
        """
        with open(self.csv_file_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writerow(record)

    @staticmethod
    def create_hand_record(
        game_number: int,
        hand_number: int,
        dealer: str,
        # Player 1
        p1_dealt_cards: str,
        p1_kept_cards: str,
        p1_discards: str,
        p1_hand_score: int,
        p1_hand_breakdown: Dict[str, int],
        p1_score_before: int,
        p1_score_after: int,
        # Player 2
        p2_dealt_cards: str,
        p2_kept_cards: str,
        p2_discards: str,
        p2_hand_score: int,
        p2_hand_breakdown: Dict[str, int],
        p2_score_before: int,
        p2_score_after: int,
        # Crib
        crib_cards: str,
        crib_score: int,
        crib_breakdown: Dict[str, int],
        # Shared
        starter_card: str,
        his_heels: bool,
    ) -> Dict:
        """Create a hand details record.

        Args:
            game_number: Game number
            hand_number: Hand number within game
            dealer: Name of dealer
            p1_dealt_cards: Player 1's 6 dealt cards (comma-separated)
            p1_kept_cards: Player 1's 4 kept cards
            p1_discards: Player 1's 2 discarded cards
            p1_hand_score: Player 1's hand score
            p1_hand_breakdown: Player 1's scoring breakdown dict
            p1_score_before: Player 1's score before this hand
            p1_score_after: Player 1's score after this hand
            p2_dealt_cards: Player 2's 6 dealt cards
            p2_kept_cards: Player 2's 4 kept cards
            p2_discards: Player 2's 2 discarded cards
            p2_hand_score: Player 2's hand score
            p2_hand_breakdown: Player 2's scoring breakdown dict
            p2_score_before: Player 2's score before this hand
            p2_score_after: Player 2's score after this hand
            crib_cards: Crib cards (4 cards)
            crib_score: Crib score
            crib_breakdown: Crib scoring breakdown dict
            starter_card: The starter card
            his_heels: Whether starter was Jack

        Returns:
            Dictionary with hand details
        """
        return {
            "game_number": game_number,
            "hand_number": hand_number,
            "dealer": dealer,
            # Player 1
            "p1_dealt_cards": p1_dealt_cards,
            "p1_kept_cards": p1_kept_cards,
            "p1_discards": p1_discards,
            "p1_hand_score": p1_hand_score,
            "p1_hand_fifteens": p1_hand_breakdown.get("fifteens", 0),
            "p1_hand_pairs": p1_hand_breakdown.get("pairs", 0),
            "p1_hand_runs": p1_hand_breakdown.get("runs", 0),
            "p1_hand_flush": p1_hand_breakdown.get("flush", 0),
            "p1_hand_nobs": p1_hand_breakdown.get("nobs", 0),
            "p1_score_before": p1_score_before,
            "p1_score_after": p1_score_after,
            # Player 2
            "p2_dealt_cards": p2_dealt_cards,
            "p2_kept_cards": p2_kept_cards,
            "p2_discards": p2_discards,
            "p2_hand_score": p2_hand_score,
            "p2_hand_fifteens": p2_hand_breakdown.get("fifteens", 0),
            "p2_hand_pairs": p2_hand_breakdown.get("pairs", 0),
            "p2_hand_runs": p2_hand_breakdown.get("runs", 0),
            "p2_hand_flush": p2_hand_breakdown.get("flush", 0),
            "p2_hand_nobs": p2_hand_breakdown.get("nobs", 0),
            "p2_score_before": p2_score_before,
            "p2_score_after": p2_score_after,
            # Crib
            "crib_cards": crib_cards,
            "crib_score": crib_score,
            "crib_fifteens": crib_breakdown.get("fifteens", 0),
            "crib_pairs": crib_breakdown.get("pairs", 0),
            "crib_runs": crib_breakdown.get("runs", 0),
            "crib_flush": crib_breakdown.get("flush", 0),
            "crib_nobs": crib_breakdown.get("nobs", 0),
            # Shared
            "starter_card": starter_card,
            "his_heels": his_heels,
        }
