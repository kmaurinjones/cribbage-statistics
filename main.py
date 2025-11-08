"""Main entry point for cribbage game simulator.

Usage:
    python main.py --n_games N [--no_track_states] [--verbosity {0,1,2}] [--debug]

Arguments:
    --n_games: Number of games to simulate (required, must be > 0)
    --no_track_states: Disable random state tracking (default: tracking enabled)
    --verbosity: Verbosity level - 0 (silent), 1 (normal), 2 (detailed) (default: 1)
    --debug: Enable debug mode with detailed internal logging (default: False)
"""

import argparse
import sys

from tqdm import tqdm

from src.game.game import Game
from src.utils.csv_exporter import CSVExporter
from src.utils.hand_details_exporter import HandDetailsExporter
from src.utils.log_manager import LogManager
from src.utils.state_tracker import StateTracker


def parse_args():
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Cribbage game simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--n_games",
        type=int,
        required=True,
        help="Number of games to simulate (must be > 0)",
    )

    parser.add_argument(
        "--no_track_states",
        action="store_true",
        default=False,
        help="Disable random state tracking (tracking is enabled by default)",
    )

    parser.add_argument(
        "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=1,
        help="Verbosity level: 0 (silent), 1 (normal), 2 (detailed)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode with detailed internal logging",
    )

    args = parser.parse_args()

    # Validate n_games
    if args.n_games <= 0:
        parser.error("--n_games must be greater than 0")

    return args


def run_simulation(
    n_games: int, track_states: bool, verbosity: int, debug: bool
) -> None:
    """Run the cribbage simulation.

    Args:
        n_games: Number of games to simulate
        track_states: Whether to track random states
        verbosity: Verbosity level (0-2)
        debug: Whether to enable debug mode
    """
    # Initialize state tracker (tracking enabled by default)
    state_tracker = StateTracker(track_states=track_states)

    # Initialize log manager and create log/CSV files
    log_manager = LogManager(base_dir="./logs")
    log_file_path = log_manager.initialize_log_file()
    csv_file_path = log_manager.initialize_csv_file(CSVExporter.FIELDNAMES)
    hand_details_path = log_manager.initialize_csv_file(
        HandDetailsExporter.FIELDNAMES, suffix="_hands"
    )

    # Initialize CSV exporters
    csv_exporter = CSVExporter(csv_file_path)
    hand_details_exporter = HandDetailsExporter(hand_details_path)

    # Statistics tracking
    player1_wins = 0
    player2_wins = 0
    total_hands = 0

    # Print and log header
    header_lines = [
        f"\n{'=' * 70}",
        "CRIBBAGE SIMULATOR",
        f"{'=' * 70}",
        f"Simulating {n_games} game{'s' if n_games > 1 else ''}",
        f"Verbosity: {verbosity}, Debug: {debug}, Track States: {track_states}",
        f"Log file: {log_file_path}",
        f"CSV file (summary): {csv_file_path}",
        f"CSV file (hands): {hand_details_path}",
        f"{'=' * 70}\n",
    ]

    for line in header_lines:
        print(line)

    # Write header to log file
    with open(log_file_path, "w") as f:
        f.write("\n".join(header_lines) + "\n")

    # Use tqdm progress bar for verbosity 0, otherwise plain loop
    game_iterator = range(1, n_games + 1)
    if verbosity == 0:
        game_iterator = tqdm(game_iterator, desc="Simulating games", unit="game")

    for game_num in game_iterator:
        # Initialize random state for this game
        random_state = state_tracker.initialize_random_state()

        # Create and play game
        game = Game(
            player1_name="Player 1",
            player2_name="Player 2",
            random_state=random_state,
            verbosity=verbosity,
            debug=debug,
            log_file=str(log_file_path),
            hand_details_exporter=hand_details_exporter,
        )
        game.game_number = game_num  # Set game number for hand tracking

        winner = game.play_game()

        # Track statistics
        if winner.name == "Player 1":
            player1_wins += 1
        else:
            player2_wins += 1

        total_hands += game.hand_number

        # Record seed for reproducibility
        state_tracker.record_game_seed()

        # Create CSV record for this game
        csv_record = CSVExporter.create_game_record(
            game_number=game_num,
            timestamp=log_manager.get_timestamp_str(),
            winner_name=winner.name,
            player1_name="Player 1",
            player1_score=game.players[0].get_score(),
            player1_play_points=game.players[0].get_play_points(),
            player1_count_points=game.players[0].get_count_points(),
            player2_name="Player 2",
            player2_score=game.players[1].get_score(),
            player2_play_points=game.players[1].get_play_points(),
            player2_count_points=game.players[1].get_count_points(),
            hands_played=game.hand_number,
            random_seed=state_tracker.get_current_seed() if track_states else None,
        )

        # Write CSV record immediately
        csv_exporter.write_record(csv_record)

        # Print game summary
        if verbosity >= 1:
            print(f"\nGame {game_num} complete:")
            scores = game.get_scores()
            for name, score in scores.items():
                print(f"  {name}: {score}")
            print(f"  Winner: {winner.name}")
            print(f"  Hands played: {game.hand_number}")

            # Print seed if tracking
            if track_states:
                seed_report = state_tracker.print_seed_report(game_num)
                print(f"  {seed_report}")

        # Separator between games
        if verbosity >= 1 and game_num < n_games:
            print(f"\n{'-' * 70}\n")

    # Print final statistics
    final_stats = [
        f"\n{'=' * 70}",
        "SIMULATION COMPLETE",
        f"{'=' * 70}",
        f"Games played: {n_games}",
        f"Player 1 wins: {player1_wins} ({player1_wins / n_games * 100:.1f}%)",
        f"Player 2 wins: {player2_wins} ({player2_wins / n_games * 100:.1f}%)",
        f"Average hands per game: {total_hands / n_games:.1f}",
    ]

    for stat in final_stats:
        print(stat)

    # Only print seeds for verbosity >= 1 (avoid flooding output for large runs)
    if track_states and verbosity >= 1:
        print("\nAll game seeds (for reproducibility):")
        for i, seed in enumerate(state_tracker.get_all_seeds(), 1):
            print(f"  Game {i}: {seed}")

    if verbosity == 0:
        # For verbosity 0, show file paths
        print("\nResults saved to:")
        print(f"  Log: {log_file_path}")
        print(f"  CSV (summary): {csv_file_path}")
        print(f"  CSV (hands): {hand_details_path}")
    else:
        # For verbosity 1+, show file paths without extra newline
        print("\nResults saved to:")
        print(f"  Log: {log_file_path}")
        print(f"  CSV (summary): {csv_file_path}")
        print(f"  CSV (hands): {hand_details_path}")

    print(f"{'=' * 70}\n")

    # Write final stats to log file
    with open(log_file_path, "a") as f:
        f.write("\n".join(final_stats) + "\n")
        if track_states:
            f.write("\nAll game seeds (for reproducibility):\n")
            for i, seed in enumerate(state_tracker.get_all_seeds(), 1):
                f.write(f"  Game {i}: {seed}\n")


def main():
    """Main entry point."""
    try:
        args = parse_args()
        run_simulation(
            n_games=args.n_games,
            track_states=not args.no_track_states,  # Invert the flag
            verbosity=args.verbosity,
            debug=args.debug,
        )
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}", file=sys.stderr)
        if "args" in locals() and args.debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
