"""CSV export utilities for game statistics."""

import csv
from pathlib import Path
from typing import Dict, List, Optional


class CSVExporter:
    """Exports game statistics to CSV files.

    Tracks detailed game information including:
    - Game number
    - Winner
    - Final scores
    - Hands played
    - Random seed (if tracking)
    - Play phase points
    - Count phase points
    """

    # CSV field names
    FIELDNAMES = [
        "game_number",
        "timestamp",
        "winner",
        "player1_final_score",
        "player2_final_score",
        "hands_played",
        "player1_play_points",
        "player1_count_points",
        "player2_play_points",
        "player2_count_points",
        "random_seed",
    ]

    def __init__(self, csv_file_path: Path):
        """Initialize CSV exporter.

        Args:
            csv_file_path: Path to CSV file
        """
        self.csv_file_path = csv_file_path
        self.game_records: List[Dict] = []

    def add_game_record(self, record: Dict) -> None:
        """Add a game record to the buffer.

        Args:
            record: Dictionary containing game statistics
        """
        self.game_records.append(record)

    def write_record(self, record: Dict) -> None:
        """Write a single record immediately to CSV.

        Args:
            record: Dictionary containing game statistics
        """
        with open(self.csv_file_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writerow(record)

    def write_all_records(self) -> None:
        """Write all buffered records to CSV."""
        if not self.game_records:
            return

        with open(self.csv_file_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writerows(self.game_records)

        self.game_records.clear()

    @staticmethod
    def create_game_record(
        game_number: int,
        timestamp: str,
        winner_name: str,
        player1_name: str,
        player1_score: int,
        player1_play_points: int,
        player1_count_points: int,
        player2_name: str,
        player2_score: int,
        player2_play_points: int,
        player2_count_points: int,
        hands_played: int,
        random_seed: Optional[int] = None,
    ) -> Dict:
        """Create a game record dictionary.

        Args:
            game_number: Game number in simulation
            timestamp: Timestamp string
            winner_name: Name of winning player
            player1_name: Name of player 1
            player1_score: Player 1 final score
            player1_play_points: Player 1 points from play phase
            player1_count_points: Player 1 points from counting phase
            player2_name: Name of player 2
            player2_score: Player 2 final score
            player2_play_points: Player 2 points from play phase
            player2_count_points: Player 2 points from counting phase
            hands_played: Number of hands in game
            random_seed: Random seed if tracking states

        Returns:
            Dictionary with game statistics
        """
        return {
            "game_number": game_number,
            "timestamp": timestamp,
            "winner": winner_name,
            "player1_final_score": player1_score,
            "player2_final_score": player2_score,
            "hands_played": hands_played,
            "player1_play_points": player1_play_points,
            "player1_count_points": player1_count_points,
            "player2_play_points": player2_play_points,
            "player2_count_points": player2_count_points,
            "random_seed": random_seed if random_seed else "",
        }
