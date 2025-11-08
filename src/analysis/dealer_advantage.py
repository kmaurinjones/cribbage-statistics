"""Analyze dealer advantage in cribbage."""

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import pandas as pd
from pathlib import Path
from typing import Dict, Optional


def analyze_dealer_advantage(
    df: pd.DataFrame, summary_df: pd.DataFrame = None
) -> Dict[str, any]:
    """Analyze dealer vs non-dealer advantage.

    Args:
        df: Hand details dataframe
        summary_df: Optional game summary dataframe for win rate analysis

    Returns:
        Dictionary with dealer advantage statistics
    """
    # Calculate average crib value
    crib_stats = {
        "mean_crib_score": df["crib_score"].mean(),
        "median_crib_score": df["crib_score"].median(),
        "max_crib_score": df["crib_score"].max(),
    }

    # Dealer hand + crib vs non-dealer hand
    dealer_scores = []
    non_dealer_scores = []

    for _, row in df.iterrows():
        if row["dealer"] == "Player 1":
            dealer_scores.append(row["p1_hand_score"] + row["crib_score"])
            non_dealer_scores.append(row["p2_hand_score"])
        else:
            dealer_scores.append(row["p2_hand_score"] + row["crib_score"])
            non_dealer_scores.append(row["p1_hand_score"])

    dealer_series = pd.Series(dealer_scores)
    non_dealer_series = pd.Series(non_dealer_scores)

    scoring_stats = {
        "dealer_avg": dealer_series.mean(),
        "non_dealer_avg": non_dealer_series.mean(),
        "dealer_advantage_points": dealer_series.mean() - non_dealer_series.mean(),
    }

    # Win rate analysis (if summary data provided)
    win_stats = {}
    if summary_df is not None:
        # This would require tracking who dealt first in each game
        # For now, we'll skip detailed win rate analysis
        pass

    return {**crib_stats, **scoring_stats, **win_stats}


def analyze_first_dealer_impact(df: pd.DataFrame) -> Dict[str, any]:
    """Analyze impact of dealing first.

    Args:
        df: Hand details dataframe

    Returns:
        Statistics on first dealer advantage
    """
    # Group by game and find first hand dealer
    first_hand = df[df["hand_number"] == 1]

    # Calculate average points scored in first hand by dealer vs non-dealer
    dealer_first_hand = []
    non_dealer_first_hand = []

    for _, row in first_hand.iterrows():
        if row["dealer"] == "Player 1":
            dealer_first_hand.append(row["p1_hand_score"] + row["crib_score"])
            non_dealer_first_hand.append(row["p2_hand_score"])
        else:
            dealer_first_hand.append(row["p2_hand_score"] + row["crib_score"])
            non_dealer_first_hand.append(row["p1_hand_score"])

    stats = {
        "dealer_first_hand_avg": pd.Series(dealer_first_hand).mean(),
        "non_dealer_first_hand_avg": pd.Series(non_dealer_first_hand).mean(),
        "first_hand_advantage": pd.Series(dealer_first_hand).mean()
        - pd.Series(non_dealer_first_hand).mean(),
    }

    return stats


def analyze_positional_scoring(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze scoring by game position (ahead/behind/tied).

    Args:
        df: Hand details dataframe

    Returns:
        DataFrame with positional scoring statistics
    """
    # Calculate position before each hand
    positions = []

    for _, row in df.iterrows():
        p1_before = row["p1_score_before"]
        p2_before = row["p2_score_before"]

        if p1_before > p2_before:
            p1_pos = "ahead"
            p2_pos = "behind"
        elif p1_before < p2_before:
            p1_pos = "behind"
            p2_pos = "ahead"
        else:
            p1_pos = "tied"
            p2_pos = "tied"

        positions.append(
            {
                "position": p1_pos,
                "hand_score": row["p1_hand_score"],
                "is_dealer": row["dealer"] == "Player 1",
            }
        )
        positions.append(
            {
                "position": p2_pos,
                "hand_score": row["p2_hand_score"],
                "is_dealer": row["dealer"] == "Player 2",
            }
        )

    pos_df = pd.DataFrame(positions)

    # Group by position and calculate average scores
    positional_stats = (
        pos_df.groupby("position")["hand_score"]
        .agg(["mean", "median", "count"])
        .reset_index()
    )

    return positional_stats


def print_dealer_advantage_report(
    df: pd.DataFrame, summary_df: pd.DataFrame = None
) -> None:
    """Print formatted dealer advantage report.

    Args:
        df: Hand details dataframe
        summary_df: Optional game summary dataframe
    """
    print("\n" + "=" * 80)
    print("DEALER ADVANTAGE ANALYSIS")
    print("=" * 80)

    # Dealer advantage
    adv_stats = analyze_dealer_advantage(df, summary_df)
    print("\nDealer vs Non-Dealer Scoring:")
    print("-" * 80)
    print(f"Average crib score:         {adv_stats['mean_crib_score']:6.2f}")
    print(f"Median crib score:          {adv_stats['median_crib_score']:6.1f}")
    print(f"Max crib score:             {adv_stats['max_crib_score']:6.0f}")
    print(f"\nDealer avg (hand + crib):   {adv_stats['dealer_avg']:6.2f}")
    print(f"Non-dealer avg (hand only): {adv_stats['non_dealer_avg']:6.2f}")
    print(
        f"Dealer advantage:           {adv_stats['dealer_advantage_points']:+6.2f} points"
    )

    # First dealer impact
    first_dealer = analyze_first_dealer_impact(df)
    print("\nFirst Hand Impact:")
    print("-" * 80)
    print(f"Dealer first hand avg:      {first_dealer['dealer_first_hand_avg']:6.2f}")
    print(
        f"Non-dealer first hand avg:  {first_dealer['non_dealer_first_hand_avg']:6.2f}"
    )
    print(
        f"First hand advantage:       {first_dealer['first_hand_advantage']:+6.2f} points"
    )

    # Positional scoring
    positional = analyze_positional_scoring(df)
    print("\nScoring by Position:")
    print("-" * 80)
    print(f"{'Position':<15} {'Avg Score':>12} {'Median':>10} {'Count':>10}")
    print("-" * 80)
    for _, row in positional.iterrows():
        print(
            f"{row['position'].capitalize():<15} "
            f"{row['mean']:>12.2f} "
            f"{row['median']:>10.1f} "
            f"{row['count']:>10.0f}"
        )

    print("\n" + "=" * 80)


def plot_dealer_advantage(df: pd.DataFrame, output_path: Optional[Path] = None) -> None:
    """Create visualization of dealer advantage.

    Args:
        df: Hand details dataframe
        output_path: Optional path to save plot
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Dealer vs non-dealer average scores
    adv_stats = analyze_dealer_advantage(df)
    categories = ["Dealer\n(Hand + Crib)", "Non-Dealer\n(Hand Only)"]
    values = [adv_stats["dealer_avg"], adv_stats["non_dealer_avg"]]

    axes[0, 0].bar(categories, values, alpha=0.7, color=["green", "blue"], edgecolor="black")
    axes[0, 0].set_ylabel("Average Points")
    axes[0, 0].set_title(
        f"Dealer vs Non-Dealer Scoring\n(Advantage: {adv_stats['dealer_advantage_points']:+.2f} points)"
    )
    axes[0, 0].grid(True, alpha=0.3, axis="y")

    # Crib score distribution
    crib_scores = df["crib_score"]
    axes[0, 1].hist(crib_scores, bins=range(0, 30), alpha=0.7, color="purple", edgecolor="black")
    axes[0, 1].set_xlabel("Crib Score")
    axes[0, 1].set_ylabel("Frequency")
    axes[0, 1].set_title(
        f"Crib Score Distribution\n(Mean: {adv_stats['mean_crib_score']:.2f}, Median: {adv_stats['median_crib_score']:.1f})"
    )
    axes[0, 1].grid(True, alpha=0.3)

    # First hand advantage
    first_dealer = analyze_first_dealer_impact(df)
    categories_first = ["Dealer\nFirst Hand", "Non-Dealer\nFirst Hand"]
    values_first = [first_dealer["dealer_first_hand_avg"], first_dealer["non_dealer_first_hand_avg"]]

    axes[1, 0].bar(categories_first, values_first, alpha=0.7, color=["darkgreen", "darkblue"], edgecolor="black")
    axes[1, 0].set_ylabel("Average Points")
    axes[1, 0].set_title(
        f"First Hand Advantage\n(Difference: {first_dealer['first_hand_advantage']:+.2f} points)"
    )
    axes[1, 0].grid(True, alpha=0.3, axis="y")

    # Positional scoring
    positional = analyze_positional_scoring(df)
    positions = positional["position"].tolist()
    means = positional["mean"].tolist()

    axes[1, 1].bar(positions, means, alpha=0.7, color="orange", edgecolor="black")
    axes[1, 1].set_xlabel("Position")
    axes[1, 1].set_ylabel("Average Hand Score")
    axes[1, 1].set_title("Average Score by Game Position")
    axes[1, 1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Plot saved to: {output_path}")
    else:
        plt.savefig("dealer_advantage.png", dpi=150, bbox_inches="tight")
        print("Plot saved to: dealer_advantage.png")

    plt.close()
