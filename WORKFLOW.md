# Cribbage Statistics Workflow

## Two-Phase Approach

### Phase 1: Data Collection (Simulation)
Run games to generate comprehensive CSV data:

```bash
# Generate data from N games
uv run main.py --n_games 1000 --verbosity 0 --track_states
```

**Outputs:**
- `logs/YYYY-MM-DD/HH-MM-SS.log` - Full game logs
- `logs/YYYY-MM-DD/HH-MM-SS_summary.csv` - Game-level statistics
- `logs/YYYY-MM-DD/HH-MM-SS_hands.csv` - Hand-level details (every hand played)

### Phase 2: Analysis
Analyze the collected data:

```bash
# Run full analysis suite
uv run analyze.py logs/YYYY-MM-DD/HH-MM-SS_hands.csv

# Or run specific analyses
uv run analyze.py logs/YYYY-MM-DD/HH-MM-SS_hands.csv --best-hands
uv run analyze.py logs/YYYY-MM-DD/HH-MM-SS_hands.csv --scoring-dist
uv run analyze.py logs/YYYY-MM-DD/HH-MM-SS_hands.csv --dealer-advantage
```

## Data Structure

### Game Summary CSV (`*_summary.csv`)
Per-game statistics:
- Winner, final scores
- Hands played
- Play vs count points breakdown
- Random seed (if tracked)

### Hand Details CSV (`*_hands.csv`)
Per-hand granular data:
- **Dealt cards** (6-card initial hands)
- **Kept cards** (4 cards after discard)
- **Discards** (2 cards to crib)
- **Starter card**
- **Hand scores** with complete breakdown (15s, pairs, runs, flush, nobs)
- **Crib scores** with breakdown
- **Scores before/after** counting
- **His heels** indicator

## Analysis Modules

### 1. Best Hands Analysis (`src/analysis/best_hands.py`)
- Top 6-card dealt hands (before discard)
- Top 4-card kept hands (with various starters)
- Expected value by hand type
- Optimal discard strategies

### 2. Scoring Distribution (`src/analysis/scoring_distribution.py`)
- Histogram of hand scores
- Most common scoring patterns
- Perfect 29 hand frequency
- Zero-point hand frequency

### 3. Positional Analysis (`src/analysis/positional.py`)
- Dealer advantage (win rate, average crib value)
- Score correlation with winning
- Comeback probabilities
- First-hand impact

### 4. Card Value Analysis (`src/analysis/card_values.py`)
- Which cards appear in highest-scoring hands
- Value of 5s vs face cards vs aces
- Optimal cards to keep/discard

## Example Workflow

```bash
# 1. Generate large dataset
uv run main.py --n_games 10000 --verbosity 0 --track_states

# 2. Analyze best hands
uv run analyze.py logs/2025-11-07/18-50-41_hands.csv --best-hands

# Output:
# Top 10 Best 6-Card Dealt Hands:
# 1. 5♠ 5♥ 5♦ J♣ 5♣ Q♠ - Avg score: 28.2 (with optimal discard)
# 2. 5♠ 5♥ 5♦ 10♣ 10♠ J♥ - Avg score: 24.8
# ...

# 3. View scoring distribution
uv run analyze.py logs/2025-11-07/18-50-41_hands.csv --scoring-dist

# Output: Score distribution plot + statistics

# 4. Check dealer advantage
uv run analyze.py logs/2025-11-07/18-50-41_hands.csv --dealer-advantage

# Output:
# Dealer win rate: 52.3%
# Non-dealer win rate: 47.7%
# Average crib value: 4.7 points
```

## Tips

**For Quick Tests:**
```bash
uv run main.py --n_games 100 --verbosity 0
```

**For Statistical Significance:**
```bash
uv run main.py --n_games 10000 --verbosity 0
```

**For Reproducibility:**
```bash
uv run main.py --n_games 1000 --track_states --verbosity 0
```

**Combining Multiple Runs:**
```bash
# Analyze all hands from a specific date
uv run analyze.py logs/2025-11-07/*_hands.csv --best-hands
```
