"""Generate comprehensive markdown reports with plots and analysis."""

import pandas as pd
from pathlib import Path
from typing import Optional

from src.analysis.best_hands import (
    analyze_best_dealt_hands,
    analyze_best_kept_hands,
    analyze_worst_dealt_hands,
    analyze_worst_kept_hands,
    analyze_middle_dealt_hands,
    analyze_middle_kept_hands,
)
from src.analysis.scoring_distribution import (
    analyze_hand_score_distribution,
    analyze_crib_score_distribution,
    analyze_scoring_breakdown,
    plot_score_distribution,
)
from src.analysis.dealer_advantage import (
    analyze_dealer_advantage,
    analyze_first_dealer_impact,
    plot_dealer_advantage,
)
from src.analysis.card_values import (
    analyze_average_score_by_card,
    analyze_five_value,
    plot_card_values,
)


def convert_unicode_suits_to_ascii(card_string: str) -> str:
    """Convert Unicode suit symbols to ASCII notation for markdown compatibility.

    Args:
        card_string: String with Unicode suits (♣, ♦, ♥, ♠)

    Returns:
        String with ASCII suit notation (C, D, H, S)
    """
    replacements = {
        "♣": "C",
        "♦": "D",
        "♥": "H",
        "♠": "S"
    }
    result = card_string
    for unicode_suit, ascii_suit in replacements.items():
        result = result.replace(unicode_suit, ascii_suit)
    return result


def generate_markdown_report(
    df: pd.DataFrame,
    output_dir: Path,
    summary_df: Optional[pd.DataFrame] = None,
) -> Path:
    """Generate comprehensive markdown report with plots.

    Args:
        df: Hand details dataframe
        output_dir: Directory to save report and plots
        summary_df: Optional game summary dataframe

    Returns:
        Path to the generated markdown file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate all plots
    score_dist_path = output_dir / "score_distribution.png"
    dealer_adv_path = output_dir / "dealer_advantage.png"
    card_values_path = output_dir / "card_values.png"

    print("Generating plots...")
    plot_score_distribution(df, score_dist_path)
    plot_dealer_advantage(df, dealer_adv_path)
    plot_card_values(df, card_values_path)

    # Run all analyses
    print("Running analyses...")
    hand_stats, _ = analyze_hand_score_distribution(df)
    crib_stats, _ = analyze_crib_score_distribution(df)
    breakdown = analyze_scoring_breakdown(df)
    best_dealt = analyze_best_dealt_hands(df, top_n=5)
    best_kept = analyze_best_kept_hands(df, top_n=5)
    worst_dealt = analyze_worst_dealt_hands(df, bottom_n=5)
    worst_kept = analyze_worst_kept_hands(df, bottom_n=5)
    middle_dealt = analyze_middle_dealt_hands(df, n=5)
    middle_kept = analyze_middle_kept_hands(df, n=5)
    dealer_stats = analyze_dealer_advantage(df, summary_df)
    first_dealer_stats = analyze_first_dealer_impact(df)
    avg_by_card = analyze_average_score_by_card(df)
    five_stats = analyze_five_value(df)

    # Build markdown content
    md_lines = []

    # Header
    md_lines.extend(
        [
            "# Cribbage Simulation Analysis Report",
            "",
            f"**Total Hands Analyzed:** {len(df):,}",
            f"**Total Games:** {df['game_number'].nunique():,}",
            "",
            "---",
            "",
        ]
    )

    # Executive Summary
    md_lines.extend(
        [
            "## Executive Summary",
            "",
            "### Key Findings",
            "",
            f"- **Average Hand Score:** {hand_stats['mean']:.2f} points",
            f"- **Average Crib Score:** {crib_stats['mean']:.2f} points",
            f"- **Dealer Advantage:** {dealer_stats['dealer_advantage_points']:+.2f} points per hand",
            f"- **Most Valuable Card:** 5 (provides {five_stats['five_advantage']:+.2f} point advantage)",
            f"- **Zero-Point Hands:** {hand_stats['zero_pct']:.2f}% of all hands",
            "",
        ]
    )

    # Best Cards
    top_card = avg_by_card.iloc[0]
    md_lines.extend(
        [
            "### Top Performing Cards",
            "",
            f"1. **{top_card['rank']}** - Average hand score of {top_card['avg_score']:.2f} when present",
        ]
    )
    for idx, row in avg_by_card.iloc[1:3].iterrows():
        md_lines.append(
            f"{idx + 1}. **{row['rank']}** - Average hand score of {row['avg_score']:.2f} when present"
        )
    md_lines.extend(["", "---", ""])

    # Scoring Distribution
    md_lines.extend(
        [
            "## Scoring Distribution",
            "",
            "### Hand Score Statistics",
            "",
            "| Statistic | Value |",
            "|-----------|-------|",
            f"| Mean      | {hand_stats['mean']:.2f} |",
            f"| Median    | {hand_stats['median']:.1f} |",
            f"| Std Dev   | {hand_stats['std']:.2f} |",
            f"| Min       | {hand_stats['min']:.0f} |",
            f"| Max       | {hand_stats['max']:.0f} |",
            "",
            f"**Notable:** {hand_stats['zero_pct']:.2f}% of hands score zero points, "
            f"while {hand_stats['perfect_29_pct']:.4f}% achieve the perfect 29.",
            "",
        ]
    )

    # Scoring breakdown
    md_lines.extend(
        [
            "### Scoring Category Breakdown",
            "",
            "| Category | Avg Points | Frequency |",
            "|----------|------------|-----------|",
        ]
    )
    for cat in breakdown.keys():
        avg_pts = breakdown[cat].mean()
        freq_pct = (breakdown[cat] > 0).sum() / len(breakdown[cat]) * 100
        md_lines.append(f"| {cat.capitalize()} | {avg_pts:.2f} | {freq_pct:.1f}% |")
    md_lines.extend(["", f"![Score Distribution]({score_dist_path.name})", "", "---", ""])

    # Dealer Advantage
    md_lines.extend(
        [
            "## Dealer Advantage",
            "",
            f"The dealer has a significant advantage of **{dealer_stats['dealer_advantage_points']:+.2f} points** per hand on average.",
            "",
            "### Why Does the Dealer Have an Advantage?",
            "",
            "The dealer's advantage comes from the **crib** - an extra hand that only the dealer scores. "
            "While both players discard 2 cards to form the crib, only the dealer counts the crib's points. "
            f"Since the average crib scores **{dealer_stats['mean_crib_score']:.2f} points**, the dealer effectively "
            f"scores from two hands (their own hand + crib) while the non-dealer scores from only one hand.",
            "",
            "Additionally, strategic discard selection means:",
            "- **Dealers** aim to discard cards that work well together (5s, pairs, runs)",
            "- **Non-dealers** try to 'balk' the crib by discarding cards unlikely to score",
            "",
            "### Breakdown",
            "",
            f"- **Dealer Average (Hand + Crib):** {dealer_stats['dealer_avg']:.2f} points",
            f"- **Non-Dealer Average (Hand Only):** {dealer_stats['non_dealer_avg']:.2f} points",
            f"- **Average Crib Score:** {dealer_stats['mean_crib_score']:.2f} points",
            f"- **Median Crib Score:** {dealer_stats['median_crib_score']:.1f} points",
            "",
            "### First Hand Impact",
            "",
            f"The advantage of dealing first is **{first_dealer_stats['first_hand_advantage']:+.2f} points** in the opening hand. "
            "This early point advantage can be crucial in close games.",
            "",
            f"![Dealer Advantage]({dealer_adv_path.name})",
            "",
            "---",
            "",
        ]
    )

    # Card Values
    md_lines.extend(
        [
            "## Card Values Analysis",
            "",
            "### Average Hand Score by Card Rank",
            "",
            "| Rank | Avg Score | Occurrences |",
            "|------|-----------|-------------|",
        ]
    )
    for _, row in avg_by_card.iterrows():
        md_lines.append(
            f"| {row['rank']} | {row['avg_score']:.2f} | {row['count']:.0f} |"
        )

    md_lines.extend(
        [
            "",
            "### The Power of 5s",
            "",
            f"Hands containing a 5 score **{five_stats['avg_with_five']:.2f} points** on average, "
            f"compared to **{five_stats['avg_without_five']:.2f} points** for hands without a 5. "
            f"This represents a **{five_stats['five_advantage']:+.2f} point advantage**.",
            "",
            "**Why are 5s so valuable?**",
            "",
            "- **Fifteen combinations:** Every face card (10, J, Q, K) combines with 5 to make 15 (worth 2 points)",
            "- **Maximum flexibility:** 5s can form 15s with more cards than any other rank",
            "- **Multiple fifteens:** A single 5 can participate in multiple fifteen combinations",
            "- **Example:** 5-10-K counts as two fifteens (5+10=15, 5+K=15) for 4 points, before counting pairs or runs",
            "",
            f"- **Hands with 5:** {five_stats['hands_with_five']:,} ({five_stats['pct_with_five']:.2f}%)",
            f"- **Hands without 5:** {five_stats['hands_without_five']:,}",
            "",
            f"![Card Values]({card_values_path.name})",
            "",
            "---",
            "",
        ]
    )

    # Hand Analysis
    md_lines.extend(
        [
            "## Hand Analysis",
            "",
            "### Top 5 Best Dealt Hands (6 cards)",
            "",
            "| Rank | Cards | Avg Score | Max Score | Count |",
            "|------|-------|-----------|-----------|-------|",
        ]
    )
    for idx, row in best_dealt.iterrows():
        md_lines.append(
            f"| {idx + 1} | {convert_unicode_suits_to_ascii(row['dealt_cards'])} | {row['avg_score']:.2f} | {row['max_score']:.0f} | {row['count']:.0f} |"
        )

    md_lines.extend(
        [
            "",
            "### Top 5 Best Kept Hands (4 cards)",
            "",
            "| Rank | Cards | Avg Score | Max Score | Count |",
            "|------|-------|-----------|-----------|-------|",
        ]
    )
    for idx, row in best_kept.iterrows():
        md_lines.append(
            f"| {idx + 1} | {convert_unicode_suits_to_ascii(row['kept_cards'])} | {row['avg_score']:.2f} | {row['max_score']:.0f} | {row['count']:.0f} |"
        )

    # Worst Hands
    md_lines.extend(
        [
            "",
            "### Bottom 5 Worst Dealt Hands (6 cards)",
            "",
            "| Rank | Cards | Avg Score | Min Score | Count |",
            "|------|-------|-----------|-----------|-------|",
        ]
    )
    for idx, row in worst_dealt.iterrows():
        md_lines.append(
            f"| {idx + 1} | {convert_unicode_suits_to_ascii(row['dealt_cards'])} | {row['avg_score']:.2f} | {row['min_score']:.0f} | {row['count']:.0f} |"
        )

    md_lines.extend(
        [
            "",
            "### Bottom 5 Worst Kept Hands (4 cards)",
            "",
            "| Rank | Cards | Avg Score | Min Score | Count |",
            "|------|-------|-----------|-----------|-------|",
        ]
    )
    for idx, row in worst_kept.iterrows():
        md_lines.append(
            f"| {idx + 1} | {convert_unicode_suits_to_ascii(row['kept_cards'])} | {row['avg_score']:.2f} | {row['min_score']:.0f} | {row['count']:.0f} |"
        )

    # Middle-tier Hands
    md_lines.extend(
        [
            "",
            "### Middle 5 Dealt Hands (6 cards)",
            "",
            "| Rank | Cards | Avg Score | Min | Max | Count |",
            "|------|-------|-----------|-----|-----|-------|",
        ]
    )
    for idx, row in middle_dealt.iterrows():
        md_lines.append(
            f"| {idx + 1} | {convert_unicode_suits_to_ascii(row['dealt_cards'])} | {row['avg_score']:.2f} | {row['min_score']:.0f} | {row['max_score']:.0f} | {row['count']:.0f} |"
        )

    md_lines.extend(
        [
            "",
            "### Middle 5 Kept Hands (4 cards)",
            "",
            "| Rank | Cards | Avg Score | Min | Max | Count |",
            "|------|-------|-----------|-----|-----|-------|",
        ]
    )
    for idx, row in middle_kept.iterrows():
        md_lines.append(
            f"| {idx + 1} | {convert_unicode_suits_to_ascii(row['kept_cards'])} | {row['avg_score']:.2f} | {row['min_score']:.0f} | {row['max_score']:.0f} | {row['count']:.0f} |"
        )

    md_lines.extend(["", "---", ""])

    # Footer
    md_lines.extend(
        [
            "## Analysis Details",
            "",
            f"- **Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Total Hands:** {len(df):,}",
            f"- **Total Games:** {df['game_number'].nunique():,}",
            f"- **Average Hands per Game:** {len(df) / df['game_number'].nunique():.1f}",
            "",
            "*Generated by Cribbage Simulator Analysis Tool*",
        ]
    )

    # Write markdown file
    report_path = output_dir / "analysis_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(md_lines))

    print(f"\nMarkdown report generated: {report_path}")
    return report_path
