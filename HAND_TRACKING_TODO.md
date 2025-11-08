# Hand-Level Tracking Implementation Guide

## Goal
Track every hand's detailed card information to answer questions like "what's empirically the best hand?"

## Current Status
✅ **Completed:**
- Game-level CSV tracking (`*_summary.csv`)
- Play vs count points breakdown
- Progress bar for verbosity 0
- Hand details CSV exporter utility (`src/utils/hand_details_exporter.py`)

🚧 **TODO:**
- Update Game class to capture hand details
- Initialize hand details CSV in main.py
- Export hand details during counting phase

## Implementation Steps

### Step 1: Update Game.__init__ to Accept Hand Details Exporter

**File:** `src/game/game.py`

Add parameter:
```python
def __init__(
    self,
    ...,
    hand_details_exporter: Optional[HandDetailsExporter] = None,
):
    ...
    self.hand_details_exporter = hand_details_exporter
```

### Step 2: Track Dealt Cards in _deal_cards()

**File:** `src/game/game.py`, method `_deal_cards()`

Currently:
```python
def _deal_cards(self) -> None:
    """Deal 6 cards to each player."""
    for _ in range(Rules.INITIAL_HAND_SIZE):
        for player in self.players:
            card = self.deck.deal_one()
            player.add_cards_to_hand([card])
```

Change to:
```python
def _deal_cards(self) -> None:
    """Deal 6 cards to each player."""
    # Track dealt cards for hand details export
    self.dealt_cards = [[], []]  # [player1_cards, player2_cards]

    for _ in range(Rules.INITIAL_HAND_SIZE):
        for idx, player in enumerate(self.players):
            card = self.deck.deal_one()
            player.add_cards_to_hand([card])
            self.dealt_cards[idx].append(card)
```

### Step 3: Track Discards in _discard_phase()

**File:** `src/game/game.py`, method `_discard_phase()`

Add tracking:
```python
def _discard_phase(self) -> None:
    """Each player discards 2 cards to the crib."""
    dealer = self.players[self.dealer_idx]
    self._log("Discard phase...", level=2)

    # Track discards for hand details export
    self.discarded_cards = [[], []]  # [player1_discards, player2_discards]

    for idx, player in enumerate(self.players):
        is_dealer = (player == dealer)
        discards = player.choose_discards(is_dealer)
        player.discard_to_crib(discards)
        self.crib.add_cards(discards)

        # Save discards
        self.discarded_cards[idx] = discards

        self._log(...)
```

### Step 4: Track "His Heels" in _cut_starter()

**File:** `src/game/game.py`, method `_cut_starter()`

Add tracking:
```python
def _cut_starter(self) -> None:
    """Cut the deck for the starter card."""
    self.starter = self.deck.deal_one()
    self._log(f"Starter card: {self.starter}", level=2)

    # Track his heels
    self.his_heels = Rules.check_his_heels(self.starter)

    if self.his_heels:
        dealer = self.players[self.dealer_idx]
        dealer.add_score(2, from_play=True)
        ...
```

### Step 5: Export Hand Details in _counting_phase()

**File:** `src/game/game.py`, method `_counting_phase()`

After counting each hand, export details:

```python
def _counting_phase(self) -> None:
    """Count hands and crib."""
    self._log("\nCounting phase...", level=1)

    non_dealer_idx = 1 - self.dealer_idx
    dealer_idx = self.dealer_idx

    # Track scores before counting
    p1_score_before = self.players[0].get_score()
    p2_score_before = self.players[1].get_score()

    # Non-dealer counts first
    non_dealer = self.players[non_dealer_idx]
    non_dealer_score, non_dealer_breakdown = Scorer.score_hand(
        non_dealer.get_play_hand(), self.starter, is_crib=False
    )
    non_dealer.add_score(non_dealer_score, from_play=False)
    ...

    # Dealer counts hand
    dealer = self.players[dealer_idx]
    dealer_score, dealer_breakdown = Scorer.score_hand(
        dealer.get_play_hand(), self.starter, is_crib=False
    )
    dealer.add_score(dealer_score, from_play=False)
    ...

    # Dealer counts crib
    crib_score, crib_breakdown = Scorer.score_hand(
        self.crib.get_cards(), self.starter, is_crib=True
    )
    dealer.add_score(crib_score, from_play=False)
    ...

    # Export hand details if exporter configured
    if self.hand_details_exporter:
        self._export_hand_details(
            p1_score_before, p2_score_before,
            non_dealer_breakdown if non_dealer_idx == 0 else dealer_breakdown,
            dealer_breakdown if dealer_idx == 1 else non_dealer_breakdown,
            crib_breakdown
        )
```

### Step 6: Add _export_hand_details() Method

**File:** `src/game/game.py`

```python
def _export_hand_details(
    self,
    p1_score_before: int,
    p2_score_before: int,
    p1_breakdown: Dict[str, int],
    p2_breakdown: Dict[str, int],
    crib_breakdown: Dict[str, int],
) -> None:
    """Export hand details to CSV.

    Args:
        p1_score_before: Player 1 score before counting
        p2_score_before: Player 2 score before counting
        p1_breakdown: Player 1 hand scoring breakdown
        p2_breakdown: Player 2 hand scoring breakdown
        crib_breakdown: Crib scoring breakdown
    """
    from src.utils.hand_details_exporter import HandDetailsExporter

    # Helper to format cards
    def cards_to_str(cards):
        return ",".join(str(c) for c in cards)

    record = HandDetailsExporter.create_hand_record(
        game_number=self.game_number,  # Need to add this attribute
        hand_number=self.hand_number,
        dealer=self.players[self.dealer_idx].name,
        # Player 1
        p1_dealt_cards=cards_to_str(self.dealt_cards[0]),
        p1_kept_cards=cards_to_str(self.players[0].get_play_hand()),
        p1_discards=cards_to_str(self.discarded_cards[0]),
        p1_hand_score=sum(p1_breakdown.values()),
        p1_hand_breakdown=p1_breakdown,
        p1_score_before=p1_score_before,
        p1_score_after=self.players[0].get_score(),
        # Player 2
        p2_dealt_cards=cards_to_str(self.dealt_cards[1]),
        p2_kept_cards=cards_to_str(self.players[1].get_play_hand()),
        p2_discards=cards_to_str(self.discarded_cards[1]),
        p2_hand_score=sum(p2_breakdown.values()),
        p2_hand_breakdown=p2_breakdown,
        p2_score_before=p2_score_before,
        p2_score_after=self.players[1].get_score(),
        # Crib
        crib_cards=cards_to_str(self.crib.get_cards()),
        crib_score=sum(crib_breakdown.values()),
        crib_breakdown=crib_breakdown,
        # Shared
        starter_card=str(self.starter),
        his_heels=self.his_heels,
    )

    self.hand_details_exporter.write_record(record)
```

### Step 7: Update main.py to Initialize Hand Details CSV

**File:** `main.py`

```python
from src.utils.hand_details_exporter import HandDetailsExporter

def run_simulation(...):
    ...
    # Initialize CSV files
    csv_file_path = log_manager.initialize_csv_file(CSVExporter.FIELDNAMES)
    hand_details_path = log_manager.initialize_csv_file(
        HandDetailsExporter.FIELDNAMES,
        suffix="_hands"  # Creates *_hands.csv
    )

    csv_exporter = CSVExporter(csv_file_path)
    hand_details_exporter = HandDetailsExporter(hand_details_path)

    for game_num in game_iterator:
        ...
        game = Game(
            ...,
            hand_details_exporter=hand_details_exporter,
        )
        game.game_number = game_num  # Set game number for export
        ...
```

### Step 8: Update LogManager to Support Suffix

**File:** `src/utils/log_manager.py`

Add suffix parameter to `initialize_csv_file()`:

```python
def initialize_csv_file(self, fieldnames: list[str], suffix: str = "") -> Path:
    """Create CSV file and write header.

    Args:
        fieldnames: List of CSV column names
        suffix: Optional suffix before .csv (e.g., "_hands")

    Returns:
        Path to the created CSV file
    """
    date_dir = self.base_dir / self.timestamp.strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)

    # Create CSV file (HH-MM-SS{suffix}.csv)
    csv_filename = self.timestamp.strftime(f"%H-%M-%S{suffix}.csv")
    csv_file_path = date_dir / csv_filename

    # Write CSV header
    import csv
    with open(csv_file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    return csv_file_path
```

## Testing

After implementation:

```bash
# Generate data with hand tracking
uv run main.py --n_games 100 --verbosity 0

# Check output files
ls -lh logs/2025-11-07/
# Should see:
# HH-MM-SS.log
# HH-MM-SS.csv          (game summaries)
# HH-MM-SS_hands.csv    (hand details)

# View hand details
head logs/2025-11-07/*_hands.csv
```

## Analysis Examples

Once implemented, you can analyze:

```python
import pandas as pd

# Load hand details
df = pd.read_csv('logs/2025-11-07/HH-MM-SS_hands.csv')

# Best 6-card dealt hands
df['p1_total_score'] = df['p1_hand_score'] + (df['crib_score'] * (df['dealer'] == 'Player 1'))
best_hands = df.nlargest(10, 'p1_total_score')[['p1_dealt_cards', 'p1_total_score']]
print("Top 10 best dealt hands:")
print(best_hands)

# Score distribution
df['p1_hand_score'].hist(bins=range(0, 30))

# Which cards to discard
# Group by dealt cards, find average score for each discard strategy
...
```

## Estimated Effort

- **Complexity**: Medium-High
- **Files to modify**: 3 (game.py, main.py, log_manager.py)
- **Lines to add**: ~150
- **Testing time**: 15-20 minutes

Ready to implement when you are!
