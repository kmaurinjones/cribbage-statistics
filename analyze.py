#!/usr/bin/env python3
"""Analyze cribbage simulation data."""

import argparse
import sys
from pathlib import Path

import pandas as pd

from src.analysis.best_hands import print_best_hands_report
from src.analysis.card_values import print_card_values_report
from src.analysis.dealer_advantage import print_dealer_advantage_report
from src.analysis.scoring_distribution import (
    plot_score_distribution,
    print_scoring_distribution_report,
)


def parse_args():
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Analyze cribbage simulation data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "hands_csv",
        type=str,
        help="Path to hand details CSV file (e.g., logs/YYYY-MM-DD/HH-MM-SS_hands.csv)",
    )

    parser.add_argument(
        "--summary_csv",
        type=str,
        help="Optional path to game summary CSV file",
    )

    parser.add_argument(
        "--best-hands",
        action="store_true",
        help="Analyze best hands",
    )

    parser.add_argument(
        "--scoring-dist",
        action="store_true",
        help="Analyze scoring distribution",
    )

    parser.add_argument(
        "--dealer-adv",
        action="store_true",
        help="Analyze dealer advantage",
    )

    parser.add_argument(
        "--card-values",
        action="store_true",
        help="Analyze card values",
    )

    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate plots (for scoring distribution only)",
    )

    parser.add_argument(
        "--create_plots",
        action="store_true",
        help="Generate comprehensive markdown report with all plots and analysis",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all analyses",
    )

    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top results to show (default: 10)",
    )

    args = parser.parse_args()

    # If no specific analysis requested, run all
    if not any(
        [
            args.best_hands,
            args.scoring_dist,
            args.dealer_adv,
            args.card_values,
            args.all,
        ]
    ):
        args.all = True

    return args


def load_data(hands_csv: str, summary_csv: str = None) -> tuple:
    """Load simulation data from CSV files.

    Args:
        hands_csv: Path to hand details CSV
        summary_csv: Optional path to game summary CSV

    Returns:
        Tuple of (hands_df, summary_df)
    """
    hands_path = Path(hands_csv)
    if not hands_path.exists():
        print(f"Error: Hand details CSV not found: {hands_path}")
        sys.exit(1)

    print(f"Loading hand details from: {hands_path}")
    hands_df = pd.read_csv(hands_path)
    print(f"Loaded {len(hands_df):,} hands")

    summary_df = None
    if summary_csv:
        summary_path = Path(summary_csv)
        if not summary_path.exists():
            print(f"Warning: Summary CSV not found: {summary_path}")
        else:
            print(f"Loading game summary from: {summary_path}")
            summary_df = pd.read_csv(summary_path)
            print(f"Loaded {len(summary_df):,} games")

    return hands_df, summary_df


def main():
    """Main entry point."""
    try:
        args = parse_args()

        # Load data
        hands_df, summary_df = load_data(args.hands_csv, args.summary_csv)

        print("\n" + "=" * 80)
        print("CRIBBAGE DATA ANALYSIS")
        print("=" * 80)
        print(f"Total hands analyzed: {len(hands_df):,}")
        print(f"Total games: {hands_df['game_number'].nunique():,}")
        print("=" * 80)

        # Run requested analyses
        if args.all or args.best_hands:
            print_best_hands_report(hands_df, top_n=args.top_n)

        if args.all or args.scoring_dist:
            print_scoring_distribution_report(hands_df)
            if args.plot:
                output_path = Path(args.hands_csv).parent / "score_distribution.png"
                plot_score_distribution(hands_df, output_path)

        if args.all or args.dealer_adv:
            print_dealer_advantage_report(hands_df, summary_df)

        if args.all or args.card_values:
            print_card_values_report(hands_df)

        # Generate comprehensive markdown report with plots if requested
        if args.create_plots:
            from src.analysis.report_generator import generate_markdown_report

            output_dir = Path(args.hands_csv).parent
            print("\nGenerating comprehensive markdown report with plots...")
            print(f"Output directory: {output_dir}")
            report_path = generate_markdown_report(hands_df, output_dir, summary_df)
            print(f"\nReport complete! Open {report_path} to view the analysis.")

        print("\nAnalysis complete!")

    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
