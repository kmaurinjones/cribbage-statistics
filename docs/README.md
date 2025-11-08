# Cribbage Game Simulator Documentation

## Overview

This cribbage simulator provides a complete, faithful implementation of two-player cribbage with accurate scoring for all game scenarios.

## Architecture

The simulator uses a class-based architecture with the following components:

### Core Classes

- **Card** (`src/card/card.py`): Represents individual playing cards
  - Properties: rank, suit, value (for counting to 31), rank_value (for run detection)
  - Face cards count as 10, Aces as 1

- **Deck** (`src/deck/deck.py`): Manages the 52-card deck
  - Shuffling with numpy random state for reproducibility
  - Dealing and tracking dealt cards

- **Hand** (`src/hand/hand.py`): Manages a player's cards
  - Adding/removing cards
  - Card queries

- **Crib** (`src/crib/crib.py`): Manages the dealer's crib
  - Receives 2 cards from each player

- **Scorer** (`src/score/scorer.py`): All scoring logic
  - Play phase scoring: 15s, pairs, runs, go, 31
  - Count phase scoring: 15s, pairs, runs, flush, nobs
  - Separate methods for play vs. count scoring

- **Rules** (`src/rules/rules.py`): Game constraints and validation
  - Winning threshold (121)
  - Play validation (can't exceed 31)
  - Go point calculation
  - His heels detection

- **Player** (`src/player/player.py`): Player behavior and state
  - Hand management
  - Score tracking
  - Discard strategy (currently random)
  - Play strategy (currently basic - first legal card)

- **Game** (`src/game/game.py`): Game orchestration
  - Complete game flow from deal to winner
  - Hand phases: deal, discard, cut, play, count
  - Turn management
  - Logging at configured verbosity

### Utilities

- **Logger** (`src/utils/logger.py`): Configurable logging
- **StateTracker** (`src/utils/state_tracker.py`): Random seed tracking for reproducibility

## Scoring Implementation

### Play Phase (Pegging)

During play, cards are played alternately, and points are scored immediately:

- **15**: When cards sum to 15, score 2 points
- **31**: When cards sum to 31, score 2 points
- **Pairs**: Same rank cards in sequence
  - Pair: 2 points
  - Triple: 6 points
  - Quadruple: 12 points
- **Runs**: 3+ consecutive ranks in any order (most recent cards)
  - Score 1 point per card in run
- **Go**: Last player to play before count exceeds 31 scores 1 point

### Count Phase

After play, hands and crib are counted with the starter card:

- **15s**: Any combination summing to 15 scores 2 points each
- **Pairs**: All pairs score 2 points each
- **Runs**: Longest run(s) score 1 point per card
  - Multiple runs of same length all count (e.g., double run of 3 = 6 points)
- **Flush**: 
  - Hand: 4 cards same suit = 4 points, 5 with starter = 5 points
  - Crib: All 5 cards same suit = 5 points (no 4-card flush in crib)
- **Nobs**: Jack of same suit as starter = 1 point

## Usage Examples

### Basic Simulation
```bash
# Run 10 games with normal output
uv run main.py --n_games 10

# Run silently (statistics only)
uv run main.py --n_games 100 --verbosity 0

# Detailed play-by-play
uv run main.py --n_games 1 --verbosity 2
```

### Reproducible Simulations
```bash
# Track random seeds for each game
uv run main.py --n_games 5 --track_states

# Output includes seeds like:
# Game 1 random seed: 1234567890
# Game 2 random seed: 987654321
# ...
```

### Debug Mode
```bash
# Enable debug logging with internal state
uv run main.py --n_games 1 --debug
```

## Future Enhancements

### High Priority
1. **Strategic AI**: Implement intelligent discard and play strategies
   - Optimal discard selection based on hand potential and crib ownership
   - Smart play decisions considering count, opponent's likely cards, and score situation

2. **Statistics Export**: Save detailed game statistics to files
   - Hand distributions
   - Scoring patterns
   - Win rates by position

### Medium Priority
3. **Multi-player Support**: Extend to 3 and 4 player games
4. **Tournament Mode**: Run brackets with multiple players
5. **Hand Analysis**: Tools to analyze specific hand scenarios

### Low Priority
6. **Different AI Levels**: Beginner, intermediate, expert AI
7. **Custom Strategies**: Allow pluggable strategy modules
8. **Visualization**: Generate game flow diagrams

## Testing

The simulator has been tested with:
- All verbosity levels (0, 1, 2)
- State tracking enabled/disabled
- Debug mode
- Multiple game simulations

All cribbage rules have been verified including:
- Proper dealing and shuffling
- Discard phase
- Starter card cut
- His heels scoring
- All play phase scoring scenarios
- All count phase scoring scenarios
- Proper turn order (non-dealer plays first, non-dealer counts first)
- Game winning conditions

## Contributing

When extending the simulator:

1. Maintain the class-based architecture
2. Keep scoring logic in the Scorer class
3. Keep rule validation in the Rules class
4. Use type hints for all function signatures
5. Add docstrings for all classes and methods
6. Test with various verbosity levels and debug mode
