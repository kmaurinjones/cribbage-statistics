# Cribbage Data Analysis Guide

## Current Data Collection

The simulator already collects detailed game statistics in CSV format. Each run creates:

**Game Summary CSV** (`logs/YYYY-MM-DD/HH-MM-SS.csv`):
```csv
game_number,timestamp,winner,player1_final_score,player2_final_score,hands_played,
player1_play_points,player1_count_points,player2_play_points,player2_count_points,random_seed
```

## Quick Start: Run & Analyze

### 1. Generate Data

```bash
# Generate 1000 games of data
uv run main.py --n_games 1000 --verbosity 0 --track_states

# Output will be at: logs/2025-11-07/HH-MM-SS.csv
```

### 2. Analyze with Pandas

```bash
# Install pandas if needed
uv add pandas matplotlib seaborn

# Start Python
uv run python
```

## Analysis Examples

### Example 1: Dealer Advantage

```python
import pandas as pd

# Load data
df = pd.read_csv('logs/2025-11-07/18-50-41.csv')

# Calculate win rates by first dealer
# (In cribbage, players alternate dealing, so dealer advantage affects outcomes)

# Simple stats
print("Player 1 win rate:", (df['winner'] == 'Player 1').mean())
print("Player 2 win rate:", (df['winner'] == 'Player 2').mean())

# Average scores
print("\nAverage final scores:")
print("Player 1:", df['player1_final_score'].mean())
print("Player 2:", df['player2_final_score'].mean())

# Play vs Count points
print("\nAverage play points:")
print("Player 1:", df['player1_play_points'].mean())
print("Player 2:", df['player2_play_points'].mean())

print("\nAverage count points:")
print("Player 1:", df['player1_count_points'].mean())
print("Player 2:", df['player2_count_points'].mean())
```

### Example 2: Score Distributions

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('logs/2025-11-07/18-50-41.csv')

# Plot final score distribution
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].hist(df['player1_final_score'], bins=30, alpha=0.7, label='Player 1')
axes[0].hist(df['player2_final_score'], bins=30, alpha=0.7, label='Player 2')
axes[0].set_xlabel('Final Score')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Final Score Distribution')
axes[0].legend()
axes[0].axvline(121, color='red', linestyle='--', label='Win threshold')

# Plot hands played distribution
axes[1].hist(df['hands_played'], bins=range(5, 25), alpha=0.7)
axes[1].set_xlabel('Hands Played')
axes[1].set_ylabel('Frequency')
axes[1].set_title('Game Length Distribution')

plt.tight_layout()
plt.savefig('score_distributions.png')
print("Saved to score_distributions.png")
```

### Example 3: Play vs Count Analysis

```python
# Which phase contributes more to winning?
df['p1_total'] = df['player1_play_points'] + df['player1_count_points']
df['p2_total'] = df['player2_play_points'] + df['player2_count_points']

df['p1_play_pct'] = df['player1_play_points'] / df['p1_total']
df['p2_play_pct'] = df['player2_play_points'] / df['p2_total']

# Split by winner
p1_wins = df[df['winner'] == 'Player 1']
p2_wins = df[df['winner'] == 'Player 2']

print("Winners' play phase percentage:")
print("Player 1 wins:", p1_wins['p1_play_pct'].mean())
print("Player 2 wins:", p2_wins['p2_play_pct'].mean())

# Correlation between play points and winning
print("\nCorrelation between play points and final score:")
print("Player 1:", df[['player1_play_points', 'player1_final_score']].corr().iloc[0, 1])
print("Player 2:", df[['player2_play_points', 'player2_final_score']].corr().iloc[0, 1])
```

### Example 4: Game Length Analysis

```python
# Do shorter games favor one player?
df['game_length_cat'] = pd.cut(df['hands_played'], bins=[0, 10, 15, 20, 100],
                                labels=['Quick (<10)', 'Normal (10-15)', 'Long (15-20)', 'Very Long (20+)'])

win_rate_by_length = df.groupby('game_length_cat')['winner'].apply(
    lambda x: (x == 'Player 1').mean()
)

print("Player 1 win rate by game length:")
print(win_rate_by_length)

# Average score margin by game length
df['score_margin'] = abs(df['player1_final_score'] - df['player2_final_score'])
print("\nAverage score margin by game length:")
print(df.groupby('game_length_cat')['score_margin'].mean())
```

## Building Custom Analysis Scripts

Create a file `my_analysis.py`:

```python
#!/usr/bin/env python3
"""Custom cribbage analysis script."""

import pandas as pd
import sys
from pathlib import Path

def analyze_dealer_advantage(csv_path):
    """Analyze dealer advantage from game data."""
    df = pd.read_csv(csv_path)

    # Your analysis here
    p1_wins = (df['winner'] == 'Player 1').sum()
    p2_wins = (df['winner'] == 'Player 2').sum()
    total = len(df)

    print(f"\n{'='*60}")
    print(f"DEALER ADVANTAGE ANALYSIS")
    print(f"{'='*60}")
    print(f"Total games analyzed: {total}")
    print(f"Player 1 wins: {p1_wins} ({p1_wins/total*100:.1f}%)")
    print(f"Player 2 wins: {p2_wins} ({p2_wins/total*100:.1f}%)")

    # More analysis...
    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python my_analysis.py <csv_file>")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        sys.exit(1)

    analyze_dealer_advantage(csv_path)
```

Run it:
```bash
uv run python my_analysis.py logs/2025-11-07/18-50-41.csv
```

## Combining Multiple Runs

```python
import pandas as pd
from glob import glob

# Load all CSVs from a directory
csv_files = glob('logs/2025-11-07/*.csv')
dfs = [pd.read_csv(f) for f in csv_files]
combined_df = pd.concat(dfs, ignore_index=True)

print(f"Total games analyzed: {len(combined_df)}")

# Run your analysis on combined data
# ...
```

## Next Steps

To answer "what's the best hand?", you'll want to enhance data collection to track:
- Individual hands dealt (6 cards)
- Cards kept (4 cards)
- Cards discarded (2 cards)
- Starter card
- Hand score with breakdown

This requires updating the Game class to export this detail. Would you like me to implement that, or are the current game-level statistics sufficient for now?
