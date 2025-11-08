"""Log file management utilities."""

from datetime import datetime
from pathlib import Path
from typing import Optional


class LogManager:
    """Manages log file creation and organization.

    Logs are stored in ./logs/YYYY-MM-DD/HH-MM-SS/ directory structure.
    A single timestamp is used for an entire simulation run.
    """

    def __init__(self, base_dir: str = "./logs"):
        """Initialize log manager.

        Args:
            base_dir: Base directory for logs (default: ./logs)
        """
        self.base_dir = Path(base_dir)
        self.timestamp = datetime.now()
        self.run_dir: Optional[Path] = None  # YYYY-MM-DD/HH-MM-SS directory
        self.log_file_path: Optional[Path] = None
        self.csv_file_path: Optional[Path] = None

    def initialize_log_file(self) -> Path:
        """Create log directory structure and log file.

        Returns:
            Path to the created log file
        """
        # Create run directory (YYYY-MM-DD/HH-MM-SS/)
        if self.run_dir is None:
            date_dir = self.base_dir / self.timestamp.strftime("%Y-%m-%d")
            time_dir = date_dir / self.timestamp.strftime("%H-%M-%S")
            time_dir.mkdir(parents=True, exist_ok=True)
            self.run_dir = time_dir

        # Create log file (simulation.log)
        self.log_file_path = self.run_dir / "simulation.log"

        # Create the log file
        self.log_file_path.touch()

        return self.log_file_path

    def initialize_csv_file(self, fieldnames: list[str], suffix: str = "") -> Path:
        """Create CSV file and write header.

        Args:
            fieldnames: List of CSV column names
            suffix: Optional suffix before .csv (e.g., "_hands" -> "hands.csv")

        Returns:
            Path to the created CSV file
        """
        # Create run directory (YYYY-MM-DD/HH-MM-SS/) if not already created
        if self.run_dir is None:
            date_dir = self.base_dir / self.timestamp.strftime("%Y-%m-%d")
            time_dir = date_dir / self.timestamp.strftime("%H-%M-%S")
            time_dir.mkdir(parents=True, exist_ok=True)
            self.run_dir = time_dir

        # Determine CSV filename based on suffix
        if suffix == "_hands":
            csv_filename = "hands.csv"
        elif not suffix:
            csv_filename = "summary.csv"
        else:
            # Custom suffix - remove leading underscore if present
            clean_suffix = suffix.lstrip("_")
            csv_filename = f"{clean_suffix}.csv"

        csv_file_path = self.run_dir / csv_filename

        # Write CSV header
        import csv

        with open(csv_file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

        # Store the summary CSV path (when suffix is empty)
        if not suffix:
            self.csv_file_path = csv_file_path

        return csv_file_path

    def get_log_file_path(self) -> Optional[Path]:
        """Get the current log file path.

        Returns:
            Path to log file or None if not initialized
        """
        return self.log_file_path

    def get_csv_file_path(self) -> Optional[Path]:
        """Get the current CSV file path.

        Returns:
            Path to CSV file or None if not initialized
        """
        return self.csv_file_path

    def get_timestamp(self) -> datetime:
        """Get the timestamp for this run.

        Returns:
            datetime object for this run
        """
        return self.timestamp

    def get_timestamp_str(self) -> str:
        """Get formatted timestamp string.

        Returns:
            Timestamp in 'YYYY-MM-DD HH:MM:SS' format
        """
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
