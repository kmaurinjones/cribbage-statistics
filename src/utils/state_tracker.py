"""State tracking utilities for reproducibility."""

import numpy as np


class StateTracker:
    """Tracks random state for reproducibility.

    When enabled, saves the initial random state seed and can report it
    at the end of each game for reproducibility.
    """

    def __init__(self, track_states: bool = False):
        """Initialize state tracker.

        Args:
            track_states: Whether to track random states
        """
        self.track_states = track_states
        self.current_seed: int = 0
        self.game_seeds: list = []

    def initialize_random_state(self) -> np.random.RandomState:
        """Create a new random state and track its seed.

        Returns:
            numpy RandomState object
        """
        if self.track_states:
            # Generate a random seed to track
            self.current_seed = np.random.randint(0, 2**31 - 1)
            random_state = np.random.RandomState(self.current_seed)
        else:
            # Use default random state without tracking
            random_state = np.random.RandomState()
            self.current_seed = 0

        return random_state

    def record_game_seed(self) -> None:
        """Record the seed for the completed game."""
        if self.track_states:
            self.game_seeds.append(self.current_seed)

    def get_current_seed(self) -> int:
        """Get the current game's seed.

        Returns:
            Current seed value
        """
        return self.current_seed

    def get_all_seeds(self) -> list:
        """Get all recorded game seeds.

        Returns:
            List of seeds for all games
        """
        return self.game_seeds.copy()

    def print_seed_report(self, game_number: int) -> str:
        """Generate a seed report for a completed game.

        Args:
            game_number: Game number for the report

        Returns:
            Formatted seed report string
        """
        if not self.track_states:
            return ""

        return f"Game {game_number} random seed: {self.current_seed}"
