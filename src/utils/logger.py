"""Logging utilities for cribbage simulator."""

import sys
from typing import TextIO


class Logger:
    """Handles logging with configurable verbosity and debug modes.

    Verbosity levels:
    - 0: Silent (no output)
    - 1: Normal (main game events, scores)
    - 2: Detailed (includes play-by-play, card details)

    Debug mode: Enables all logging plus internal state details
    """

    def __init__(
        self, verbosity: int = 1, debug: bool = False, output: TextIO = sys.stdout
    ):
        """Initialize logger.

        Args:
            verbosity: Verbosity level (0=silent, 1=normal, 2=detailed)
            debug: Enable debug mode
            output: Output stream (default stdout)
        """
        self.verbosity = max(0, min(2, verbosity))  # Clamp to [0, 2]
        self.debug = debug
        self.output = output

    def log(self, message: str, level: int = 1, debug_only: bool = False) -> None:
        """Log a message based on verbosity settings.

        Args:
            message: Message to log
            level: Minimum verbosity level required (0, 1, 2)
            debug_only: Only log if debug mode is enabled
        """
        if debug_only and not self.debug:
            return

        if self.verbosity >= level or self.debug:
            print(message, file=self.output)

    def log_debug(self, message: str) -> None:
        """Log a debug message (only in debug mode).

        Args:
            message: Debug message to log
        """
        if self.debug:
            print(f"[DEBUG] {message}", file=self.output)

    def log_error(self, message: str) -> None:
        """Log an error message (always shown).

        Args:
            message: Error message to log
        """
        print(f"[ERROR] {message}", file=sys.stderr)

    def set_verbosity(self, verbosity: int) -> None:
        """Update verbosity level.

        Args:
            verbosity: New verbosity level (0-2)
        """
        self.verbosity = max(0, min(2, verbosity))

    def set_debug(self, debug: bool) -> None:
        """Update debug mode.

        Args:
            debug: Enable/disable debug mode
        """
        self.debug = debug
