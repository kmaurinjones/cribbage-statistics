"""Analyze best cribbage hands from simulation data."""

import pandas as pd


def analyze_best_dealt_hands(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Find the best 6-card dealt hands.

    Args:
        df: Hand details dataframe
        top_n: Number of top hands to return

    Returns:
        DataFrame with top dealt hands and their average scores
    """
    # Calculate total value for each player (hand + crib if dealer)
    p1_total = df.copy()
    p1_total["is_dealer"] = df["dealer"] == "Player 1"
    p1_total["total_score"] = p1_total["p1_hand_score"] + p1_total.apply(
        lambda row: row["crib_score"] if row["is_dealer"] else 0, axis=1
    )
    p1_total["dealt_cards"] = p1_total["p1_dealt_cards"]

    p2_total = df.copy()
    p2_total["is_dealer"] = df["dealer"] == "Player 2"
    p2_total["total_score"] = p2_total["p2_hand_score"] + p2_total.apply(
        lambda row: row["crib_score"] if row["is_dealer"] else 0, axis=1
    )
    p2_total["dealt_cards"] = p2_total["p2_dealt_cards"]

    # Combine both players
    all_hands = pd.concat(
        [
            p1_total[["dealt_cards", "total_score"]],
            p2_total[["dealt_cards", "total_score"]],
        ]
    )

    # Group by dealt cards and calculate stats
    best_hands = (
        all_hands.groupby("dealt_cards")
        .agg(
            avg_score=("total_score", "mean"),
            max_score=("total_score", "max"),
            count=("total_score", "count"),
        )
        .reset_index()
        .sort_values("avg_score", ascending=False)
        .head(top_n)
    )

    return best_hands


def analyze_best_kept_hands(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Find the best 4-card kept hands.

    Args:
        df: Hand details dataframe
        top_n: Number of top hands to return

    Returns:
        DataFrame with top kept hands and their average scores
    """
    # Combine both players' kept hands
    p1_hands = df[["p1_kept_cards", "p1_hand_score"]].rename(
        columns={"p1_kept_cards": "kept_cards", "p1_hand_score": "hand_score"}
    )
    p2_hands = df[["p2_kept_cards", "p2_hand_score"]].rename(
        columns={"p2_kept_cards": "kept_cards", "p2_hand_score": "hand_score"}
    )

    all_kept = pd.concat([p1_hands, p2_hands])

    # Group by kept cards and calculate stats
    best_kept = (
        all_kept.groupby("kept_cards")
        .agg(
            avg_score=("hand_score", "mean"),
            max_score=("hand_score", "max"),
            count=("hand_score", "count"),
        )
        .reset_index()
        .sort_values("avg_score", ascending=False)
        .head(top_n)
    )

    return best_kept


def analyze_discard_strategy(
    df: pd.DataFrame, dealt_hand: str, top_n: int = 5
) -> pd.DataFrame:
    """Analyze discard strategies for a specific dealt hand.

    Args:
        df: Hand details dataframe
        dealt_hand: Specific 6-card dealt hand to analyze
        top_n: Number of top discard strategies to return

    Returns:
        DataFrame with discard strategies and their outcomes
    """
    # Filter for this specific dealt hand
    p1_mask = df["p1_dealt_cards"] == dealt_hand
    p2_mask = df["p2_dealt_cards"] == dealt_hand

    p1_discards = df[p1_mask][["p1_discards", "p1_hand_score"]].rename(
        columns={"p1_discards": "discards", "p1_hand_score": "hand_score"}
    )
    p2_discards = df[p2_mask][["p2_discards", "p2_hand_score"]].rename(
        columns={"p2_discards": "discards", "p2_hand_score": "hand_score"}
    )

    all_discards = pd.concat([p1_discards, p2_discards])

    if len(all_discards) == 0:
        return pd.DataFrame()

    # Group by discard strategy
    strategy_analysis = (
        all_discards.groupby("discards")
        .agg(
            avg_score=("hand_score", "mean"),
            max_score=("hand_score", "max"),
            count=("hand_score", "count"),
        )
        .reset_index()
        .sort_values("avg_score", ascending=False)
        .head(top_n)
    )

    return strategy_analysis


def analyze_worst_dealt_hands(df: pd.DataFrame, bottom_n: int = 10) -> pd.DataFrame:
    """Find the worst 6-card dealt hands.

    Args:
        df: Hand details dataframe
        bottom_n: Number of bottom hands to return

    Returns:
        DataFrame with worst dealt hands and their average scores
    """
    # Calculate total value for each player (hand + crib if dealer)
    p1_total = df.copy()
    p1_total["is_dealer"] = df["dealer"] == "Player 1"
    p1_total["total_score"] = p1_total["p1_hand_score"] + p1_total.apply(
        lambda row: row["crib_score"] if row["is_dealer"] else 0, axis=1
    )
    p1_total["dealt_cards"] = p1_total["p1_dealt_cards"]

    p2_total = df.copy()
    p2_total["is_dealer"] = df["dealer"] == "Player 2"
    p2_total["total_score"] = p2_total["p2_hand_score"] + p2_total.apply(
        lambda row: row["crib_score"] if row["is_dealer"] else 0, axis=1
    )
    p2_total["dealt_cards"] = p2_total["p2_dealt_cards"]

    # Combine both players
    all_hands = pd.concat(
        [
            p1_total[["dealt_cards", "total_score"]],
            p2_total[["dealt_cards", "total_score"]],
        ]
    )

    # Group by dealt cards and calculate stats
    worst_hands = (
        all_hands.groupby("dealt_cards")
        .agg(
            avg_score=("total_score", "mean"),
            min_score=("total_score", "min"),
            count=("total_score", "count"),
        )
        .reset_index()
        .sort_values("avg_score", ascending=True)
        .head(bottom_n)
    )

    return worst_hands


def analyze_worst_kept_hands(df: pd.DataFrame, bottom_n: int = 10) -> pd.DataFrame:
    """Find the worst 4-card kept hands.

    Args:
        df: Hand details dataframe
        bottom_n: Number of bottom hands to return

    Returns:
        DataFrame with worst kept hands and their average scores
    """
    # Combine both players' kept hands
    p1_hands = df[["p1_kept_cards", "p1_hand_score"]].rename(
        columns={"p1_kept_cards": "kept_cards", "p1_hand_score": "hand_score"}
    )
    p2_hands = df[["p2_kept_cards", "p2_hand_score"]].rename(
        columns={"p2_kept_cards": "kept_cards", "p2_hand_score": "hand_score"}
    )

    all_kept = pd.concat([p1_hands, p2_hands])

    # Group by kept cards and calculate stats
    worst_kept = (
        all_kept.groupby("kept_cards")
        .agg(
            avg_score=("hand_score", "mean"),
            min_score=("hand_score", "min"),
            count=("hand_score", "count"),
        )
        .reset_index()
        .sort_values("avg_score", ascending=True)
        .head(bottom_n)
    )

    return worst_kept


def analyze_middle_dealt_hands(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Find middle-tier 6-card dealt hands.

    Args:
        df: Hand details dataframe
        n: Number of middle hands to return

    Returns:
        DataFrame with middle-tier dealt hands and their average scores
    """
    # Calculate total value for each player (hand + crib if dealer)
    p1_total = df.copy()
    p1_total["is_dealer"] = df["dealer"] == "Player 1"
    p1_total["total_score"] = p1_total["p1_hand_score"] + p1_total.apply(
        lambda row: row["crib_score"] if row["is_dealer"] else 0, axis=1
    )
    p1_total["dealt_cards"] = p1_total["p1_dealt_cards"]

    p2_total = df.copy()
    p2_total["is_dealer"] = df["dealer"] == "Player 2"
    p2_total["total_score"] = p2_total["p2_hand_score"] + p2_total.apply(
        lambda row: row["crib_score"] if row["is_dealer"] else 0, axis=1
    )
    p2_total["dealt_cards"] = p2_total["p2_dealt_cards"]

    # Combine both players
    all_hands = pd.concat(
        [
            p1_total[["dealt_cards", "total_score"]],
            p2_total[["dealt_cards", "total_score"]],
        ]
    )

    # Group by dealt cards and calculate stats
    all_dealt = (
        all_hands.groupby("dealt_cards")
        .agg(
            avg_score=("total_score", "mean"),
            min_score=("total_score", "min"),
            max_score=("total_score", "max"),
            count=("total_score", "count"),
        )
        .reset_index()
        .sort_values("avg_score", ascending=False)
    )

    # Get middle section
    total_count = len(all_dealt)
    middle_start = (total_count // 2) - (n // 2)
    middle_end = middle_start + n

    middle_hands = all_dealt.iloc[middle_start:middle_end]

    return middle_hands


def analyze_middle_kept_hands(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Find middle-tier 4-card kept hands.

    Args:
        df: Hand details dataframe
        n: Number of middle hands to return

    Returns:
        DataFrame with middle-tier kept hands and their average scores
    """
    # Combine both players' kept hands
    p1_hands = df[["p1_kept_cards", "p1_hand_score"]].rename(
        columns={"p1_kept_cards": "kept_cards", "p1_hand_score": "hand_score"}
    )
    p2_hands = df[["p2_kept_cards", "p2_hand_score"]].rename(
        columns={"p2_kept_cards": "kept_cards", "p2_hand_score": "hand_score"}
    )

    all_kept = pd.concat([p1_hands, p2_hands])

    # Group by kept cards and calculate stats
    all_kept_grouped = (
        all_kept.groupby("kept_cards")
        .agg(
            avg_score=("hand_score", "mean"),
            min_score=("hand_score", "min"),
            max_score=("hand_score", "max"),
            count=("hand_score", "count"),
        )
        .reset_index()
        .sort_values("avg_score", ascending=False)
    )

    # Get middle section
    total_count = len(all_kept_grouped)
    middle_start = (total_count // 2) - (n // 2)
    middle_end = middle_start + n

    middle_hands = all_kept_grouped.iloc[middle_start:middle_end]

    return middle_hands


def print_best_hands_report(df: pd.DataFrame, top_n: int = 10) -> None:
    """Print a formatted report of best hands.

    Args:
        df: Hand details dataframe
        top_n: Number of top hands to show
    """
    print("\n" + "=" * 80)
    print("BEST HANDS ANALYSIS")
    print("=" * 80)

    # Best dealt hands
    print(f"\nTop {top_n} Best 6-Card Dealt Hands:")
    print("-" * 80)
    best_dealt = analyze_best_dealt_hands(df, top_n)
    for idx, row in best_dealt.iterrows():
        print(
            f"{idx + 1:2d}. {row['dealt_cards']:30s} | "
            f"Avg: {row['avg_score']:5.2f} | "
            f"Max: {row['max_score']:2.0f} | "
            f"Count: {row['count']:4.0f}"
        )

    # Best kept hands
    print(f"\nTop {top_n} Best 4-Card Kept Hands:")
    print("-" * 80)
    best_kept = analyze_best_kept_hands(df, top_n)
    for idx, row in best_kept.iterrows():
        print(
            f"{idx + 1:2d}. {row['kept_cards']:25s} | "
            f"Avg: {row['avg_score']:5.2f} | "
            f"Max: {row['max_score']:2.0f} | "
            f"Count: {row['count']:4.0f}"
        )

    print("\n" + "=" * 80)
