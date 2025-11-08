"""Analyze individual card values in cribbage hands."""

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import pandas as pd
from collections import Counter
from pathlib import Path
from typing import Dict, Optional


def parse_cards(card_string: str) -> list:
    """Parse comma-separated card string into list.

    Args:
        card_string: Comma-separated cards (e.g., "5♠,5♥,5♦,J♣")

    Returns:
        List of card strings
    """
    return [c.strip() for c in card_string.split(",")]


def extract_card_rank(card: str) -> str:
    """Extract rank from card string.

    Args:
        card: Card string (e.g., "5♠")

    Returns:
        Rank (e.g., "5")
    """
    return card[:-1]  # Remove suit symbol


def analyze_card_frequency_in_high_hands(
    df: pd.DataFrame, threshold: int = 15, top_n: int = 13
) -> pd.DataFrame:
    """Analyze which cards appear most in high-scoring hands.

    Args:
        df: Hand details dataframe
        threshold: Score threshold for "high" hands
        top_n: Number of top cards to return

    Returns:
        DataFrame with card frequencies
    """
    # Collect all cards from high-scoring kept hands
    high_hands = []

    # Player 1 high hands
    p1_high = df[df["p1_hand_score"] >= threshold]
    for cards_str in p1_high["p1_kept_cards"]:
        high_hands.extend(parse_cards(cards_str))

    # Player 2 high hands
    p2_high = df[df["p2_hand_score"] >= threshold]
    for cards_str in p2_high["p2_kept_cards"]:
        high_hands.extend(parse_cards(cards_str))

    # Count card ranks (not suits)
    ranks = [extract_card_rank(card) for card in high_hands]
    rank_counts = Counter(ranks)

    # Create DataFrame
    freq_df = pd.DataFrame(
        [
            {"rank": rank, "count": count, "pct": count / len(ranks) * 100}
            for rank, count in rank_counts.most_common(top_n)
        ]
    )

    return freq_df


def analyze_average_score_by_card(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze average hand score when each card rank is present.

    Args:
        df: Hand details dataframe

    Returns:
        DataFrame with average scores by card rank
    """
    rank_scores = {
        rank: []
        for rank in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    }

    # Analyze both players
    for _, row in df.iterrows():
        # Player 1
        p1_cards = parse_cards(row["p1_kept_cards"])
        p1_ranks = [extract_card_rank(c) for c in p1_cards]
        for rank in set(p1_ranks):
            rank_scores[rank].append(row["p1_hand_score"])

        # Player 2
        p2_cards = parse_cards(row["p2_kept_cards"])
        p2_ranks = [extract_card_rank(c) for c in p2_cards]
        for rank in set(p2_ranks):
            rank_scores[rank].append(row["p2_hand_score"])

    # Calculate averages
    avg_scores = [
        {
            "rank": rank,
            "avg_score": pd.Series(scores).mean(),
            "count": len(scores),
        }
        for rank, scores in rank_scores.items()
    ]

    score_df = pd.DataFrame(avg_scores).sort_values("avg_score", ascending=False)

    return score_df


def analyze_five_value(df: pd.DataFrame) -> Dict[str, any]:
    """Special analysis for 5s (most valuable card).

    Args:
        df: Hand details dataframe

    Returns:
        Dictionary with 5-specific statistics
    """
    # Hands with vs without 5s
    with_five = []
    without_five = []

    for _, row in df.iterrows():
        # Player 1
        p1_cards = parse_cards(row["p1_kept_cards"])
        p1_ranks = [extract_card_rank(c) for c in p1_cards]
        if "5" in p1_ranks:
            with_five.append(row["p1_hand_score"])
        else:
            without_five.append(row["p1_hand_score"])

        # Player 2
        p2_cards = parse_cards(row["p2_kept_cards"])
        p2_ranks = [extract_card_rank(c) for c in p2_cards]
        if "5" in p2_ranks:
            with_five.append(row["p2_hand_score"])
        else:
            without_five.append(row["p2_hand_score"])

    stats = {
        "avg_with_five": pd.Series(with_five).mean(),
        "avg_without_five": pd.Series(without_five).mean(),
        "five_advantage": pd.Series(with_five).mean() - pd.Series(without_five).mean(),
        "hands_with_five": len(with_five),
        "hands_without_five": len(without_five),
        "pct_with_five": len(with_five) / (len(with_five) + len(without_five)) * 100,
    }

    return stats


def print_card_values_report(df: pd.DataFrame) -> None:
    """Print formatted card values report.

    Args:
        df: Hand details dataframe
    """
    print("\n" + "=" * 80)
    print("CARD VALUES ANALYSIS")
    print("=" * 80)

    # Card frequency in high hands
    print("\nCard Rank Frequency in High-Scoring Hands (≥15 points):")
    print("-" * 80)
    freq_df = analyze_card_frequency_in_high_hands(df, threshold=15)
    print(f"{'Rank':<8} {'Count':>10} {'Percentage':>12}")
    print("-" * 80)
    for _, row in freq_df.iterrows():
        print(f"{row['rank']:<8} {row['count']:>10.0f} {row['pct']:>11.2f}%")

    # Average score by card
    print("\nAverage Hand Score When Card is Present:")
    print("-" * 80)
    avg_df = analyze_average_score_by_card(df)
    print(f"{'Rank':<8} {'Avg Score':>12} {'Count':>10}")
    print("-" * 80)
    for _, row in avg_df.iterrows():
        print(f"{row['rank']:<8} {row['avg_score']:>12.2f} {row['count']:>10.0f}")

    # Special analysis for 5s
    five_stats = analyze_five_value(df)
    print("\nSpecial Analysis: The Value of 5s:")
    print("-" * 80)
    print(f"Avg score with 5:       {five_stats['avg_with_five']:6.2f}")
    print(f"Avg score without 5:    {five_stats['avg_without_five']:6.2f}")
    print(f"Five advantage:         {five_stats['five_advantage']:+6.2f} points")
    print(
        f"Hands with 5:           {five_stats['hands_with_five']:6.0f} ({five_stats['pct_with_five']:5.2f}%)"
    )
    print(f"Hands without 5:        {five_stats['hands_without_five']:6.0f}")

    print("\n" + "=" * 80)


def plot_card_values(df: pd.DataFrame, output_path: Optional[Path] = None) -> None:
    """Create visualization of card values.

    Args:
        df: Hand details dataframe
        output_path: Optional path to save plot
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Card frequency in high hands
    freq_df = analyze_card_frequency_in_high_hands(df, threshold=15)
    if len(freq_df) > 0:
        axes[0, 0].bar(
            freq_df["rank"], freq_df["pct"], alpha=0.7, color="purple", edgecolor="black"
        )
        axes[0, 0].set_xlabel("Card Rank")
        axes[0, 0].set_ylabel("Percentage (%)")
        axes[0, 0].set_title("Card Frequency in High-Scoring Hands (≥15 points)")
        axes[0, 0].grid(True, alpha=0.3, axis="y")
    else:
        axes[0, 0].text(0.5, 0.5, "No hands ≥15 points\nin dataset",
                       ha="center", va="center", transform=axes[0, 0].transAxes,
                       fontsize=12)
        axes[0, 0].set_title("Card Frequency in High-Scoring Hands (≥15 points)")

    # Average score by card rank
    avg_df = analyze_average_score_by_card(df)
    axes[0, 1].bar(
        avg_df["rank"], avg_df["avg_score"], alpha=0.7, color="green", edgecolor="black"
    )
    axes[0, 1].set_xlabel("Card Rank")
    axes[0, 1].set_ylabel("Average Hand Score")
    axes[0, 1].set_title("Average Hand Score When Card is Present")
    axes[0, 1].grid(True, alpha=0.3, axis="y")

    # Value of 5s comparison
    five_stats = analyze_five_value(df)
    categories = ["With 5", "Without 5"]
    values = [five_stats["avg_with_five"], five_stats["avg_without_five"]]

    axes[1, 0].bar(categories, values, alpha=0.7, color=["darkgreen", "darkred"], edgecolor="black")
    axes[1, 0].set_ylabel("Average Hand Score")
    axes[1, 0].set_title(
        f"The Value of 5s\n(Advantage: {five_stats['five_advantage']:+.2f} points)"
    )
    axes[1, 0].grid(True, alpha=0.3, axis="y")

    # Card rank occurrence counts (sorted by count descending)
    count_sorted_df = avg_df.sort_values("count", ascending=False)
    axes[1, 1].bar(
        count_sorted_df["rank"], count_sorted_df["count"], alpha=0.7, color="orange", edgecolor="black"
    )
    axes[1, 1].set_xlabel("Card Rank")
    axes[1, 1].set_ylabel("Occurrences")
    axes[1, 1].set_title("Card Rank Occurrence in All Hands")
    axes[1, 1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Plot saved to: {output_path}")
    else:
        plt.savefig("card_values.png", dpi=150, bbox_inches="tight")
        print("Plot saved to: card_values.png")

    plt.close()
