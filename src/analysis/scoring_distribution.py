"""Analyze scoring distributions in cribbage hands."""

import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict


def analyze_hand_score_distribution(df: pd.DataFrame) -> Dict[str, any]:
    """Analyze distribution of hand scores.

    Args:
        df: Hand details dataframe

    Returns:
        Dictionary with distribution statistics
    """
    # Combine all hand scores (excluding cribs)
    all_hand_scores = pd.concat([df["p1_hand_score"], df["p2_hand_score"]])

    stats = {
        "mean": all_hand_scores.mean(),
        "median": all_hand_scores.median(),
        "std": all_hand_scores.std(),
        "min": all_hand_scores.min(),
        "max": all_hand_scores.max(),
        "zero_count": (all_hand_scores == 0).sum(),
        "zero_pct": (all_hand_scores == 0).sum() / len(all_hand_scores) * 100,
        "perfect_29_count": (all_hand_scores == 29).sum(),
        "perfect_29_pct": (all_hand_scores == 29).sum() / len(all_hand_scores) * 100,
    }

    return stats, all_hand_scores


def analyze_crib_score_distribution(df: pd.DataFrame) -> Dict[str, any]:
    """Analyze distribution of crib scores.

    Args:
        df: Hand details dataframe

    Returns:
        Dictionary with distribution statistics
    """
    crib_scores = df["crib_score"]

    stats = {
        "mean": crib_scores.mean(),
        "median": crib_scores.median(),
        "std": crib_scores.std(),
        "min": crib_scores.min(),
        "max": crib_scores.max(),
        "zero_count": (crib_scores == 0).sum(),
        "zero_pct": (crib_scores == 0).sum() / len(crib_scores) * 100,
    }

    return stats, crib_scores


def analyze_scoring_breakdown(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Analyze contribution of each scoring category.

    Args:
        df: Hand details dataframe

    Returns:
        Dictionary of Series for each scoring category
    """
    # Combine both players' scoring breakdowns
    all_fifteens = pd.concat([df["p1_hand_fifteens"], df["p2_hand_fifteens"]])
    all_pairs = pd.concat([df["p1_hand_pairs"], df["p2_hand_pairs"]])
    all_runs = pd.concat([df["p1_hand_runs"], df["p2_hand_runs"]])
    all_flush = pd.concat([df["p1_hand_flush"], df["p2_hand_flush"]])
    all_nobs = pd.concat([df["p1_hand_nobs"], df["p2_hand_nobs"]])

    breakdown = {
        "fifteens": all_fifteens,
        "pairs": all_pairs,
        "runs": all_runs,
        "flush": all_flush,
        "nobs": all_nobs,
    }

    return breakdown


def plot_score_distribution(df: pd.DataFrame, output_path: Path = None) -> None:
    """Create visualization of score distributions.

    Args:
        df: Hand details dataframe
        output_path: Optional path to save plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Hand score distribution
    hand_stats, hand_scores = analyze_hand_score_distribution(df)
    axes[0, 0].hist(hand_scores, bins=range(0, 30), alpha=0.7, edgecolor="black")
    axes[0, 0].set_xlabel("Hand Score")
    axes[0, 0].set_ylabel("Frequency")
    axes[0, 0].set_title(
        f"Hand Score Distribution\n(Mean: {hand_stats['mean']:.2f}, Median: {hand_stats['median']:.1f})"
    )
    axes[0, 0].grid(True, alpha=0.3)

    # Crib score distribution
    crib_stats, crib_scores = analyze_crib_score_distribution(df)
    axes[0, 1].hist(
        crib_scores, bins=range(0, 30), alpha=0.7, color="green", edgecolor="black"
    )
    axes[0, 1].set_xlabel("Crib Score")
    axes[0, 1].set_ylabel("Frequency")
    axes[0, 1].set_title(
        f"Crib Score Distribution\n(Mean: {crib_stats['mean']:.2f}, Median: {crib_stats['median']:.1f})"
    )
    axes[0, 1].grid(True, alpha=0.3)

    # Scoring breakdown contributions
    breakdown = analyze_scoring_breakdown(df)
    categories = list(breakdown.keys())
    avg_contributions = [breakdown[cat].mean() for cat in categories]

    axes[1, 0].bar(
        categories, avg_contributions, alpha=0.7, color="purple", edgecolor="black"
    )
    axes[1, 0].set_xlabel("Scoring Category")
    axes[1, 0].set_ylabel("Average Points Per Hand")
    axes[1, 0].set_title("Average Contribution by Scoring Category")
    axes[1, 0].grid(True, alpha=0.3, axis="y")

    # Scoring breakdown frequency (% of hands with points from each category)
    freq_contributions = [
        (breakdown[cat] > 0).sum() / len(breakdown[cat]) * 100 for cat in categories
    ]

    axes[1, 1].bar(
        categories, freq_contributions, alpha=0.7, color="orange", edgecolor="black"
    )
    axes[1, 1].set_xlabel("Scoring Category")
    axes[1, 1].set_ylabel("% of Hands")
    axes[1, 1].set_title("Frequency of Points from Each Category")
    axes[1, 1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Plot saved to: {output_path}")
    else:
        plt.savefig("score_distribution.png", dpi=150, bbox_inches="tight")
        print("Plot saved to: score_distribution.png")

    plt.close()


def print_scoring_distribution_report(df: pd.DataFrame) -> None:
    """Print formatted scoring distribution report.

    Args:
        df: Hand details dataframe
    """
    print("\n" + "=" * 80)
    print("SCORING DISTRIBUTION ANALYSIS")
    print("=" * 80)

    # Hand scores
    hand_stats, _ = analyze_hand_score_distribution(df)
    print("\nHand Score Statistics:")
    print("-" * 80)
    print(f"Mean:                {hand_stats['mean']:6.2f}")
    print(f"Median:              {hand_stats['median']:6.1f}")
    print(f"Std Dev:             {hand_stats['std']:6.2f}")
    print(f"Min:                 {hand_stats['min']:6.0f}")
    print(f"Max:                 {hand_stats['max']:6.0f}")
    print(
        f"Zero-point hands:    {hand_stats['zero_count']:6.0f} ({hand_stats['zero_pct']:5.2f}%)"
    )
    print(
        f"Perfect 29 hands:    {hand_stats['perfect_29_count']:6.0f} ({hand_stats['perfect_29_pct']:5.2f}%)"
    )

    # Crib scores
    crib_stats, _ = analyze_crib_score_distribution(df)
    print("\nCrib Score Statistics:")
    print("-" * 80)
    print(f"Mean:                {crib_stats['mean']:6.2f}")
    print(f"Median:              {crib_stats['median']:6.1f}")
    print(f"Std Dev:             {crib_stats['std']:6.2f}")
    print(f"Min:                 {crib_stats['min']:6.0f}")
    print(f"Max:                 {crib_stats['max']:6.0f}")
    print(
        f"Zero-point cribs:    {crib_stats['zero_count']:6.0f} ({crib_stats['zero_pct']:5.2f}%)"
    )

    # Scoring breakdown
    breakdown = analyze_scoring_breakdown(df)
    print("\nScoring Category Breakdown:")
    print("-" * 80)
    print(f"{'Category':<15} {'Avg Points':>12} {'Frequency':>12}")
    print("-" * 80)
    for cat in breakdown.keys():
        avg_pts = breakdown[cat].mean()
        freq_pct = (breakdown[cat] > 0).sum() / len(breakdown[cat]) * 100
        print(f"{cat.capitalize():<15} {avg_pts:>12.2f} {freq_pct:>11.1f}%")

    print("\n" + "=" * 80)
