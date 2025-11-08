"""Game class for managing a complete cribbage game."""

import numpy as np
from typing import List, Optional, Dict, Tuple
from src.card.card import Card
from src.deck.deck import Deck
from src.player.player import Player
from src.crib.crib import Crib
from src.score.scorer import Scorer
from src.rules.rules import Rules


class Game:
    """Manages a complete two-player cribbage game.

    Handles:
    - Game initialization and setup
    - Dealing and shuffling
    - Play phase (pegging)
    - Counting phase
    - Score tracking
    - Winner determination
    """

    def __init__(
        self,
        player1_name: str = "Player 1",
        player2_name: str = "Player 2",
        random_state: Optional[np.random.RandomState] = None,
        verbosity: int = 1,
        debug: bool = False,
        log_file: Optional[str] = None,
        hand_details_exporter=None,
    ):
        """Initialize a cribbage game.

        Args:
            player1_name: Name for player 1
            player2_name: Name for player 2
            random_state: Optional numpy RandomState for reproducibility
            verbosity: Verbosity level (0=silent, 1=normal, 2=detailed)
            debug: Whether to enable debug logging
            log_file: Optional path to log file for writing game logs
            hand_details_exporter: Optional HandDetailsExporter for hand-level CSV tracking
        """
        self.random_state = (
            random_state if random_state is not None else np.random.RandomState()
        )
        self.verbosity = verbosity
        self.debug = debug
        self.log_file = log_file
        self.hand_details_exporter = hand_details_exporter

        # Initialize players
        self.players = [
            Player(player1_name, self.random_state),
            Player(player2_name, self.random_state),
        ]

        # Game state
        self.deck = Deck(self.random_state)
        self.crib = Crib()
        self.starter: Optional[Card] = None
        self.dealer_idx = self.random_state.choice([0, 1])  # Random first dealer
        self.hand_number = 0
        self.winner: Optional[Player] = None
        self.game_number = 0  # Set by caller for tracking

        # Hand tracking for export
        self.dealt_cards: List[List[Card]] = [[], []]  # [player1_cards, player2_cards]
        self.discarded_cards: List[List[Card]] = [
            [],
            [],
        ]  # [player1_discards, player2_discards]
        self.his_heels = False

        self._log(
            f"Game initialized. {self.players[self.dealer_idx].name} deals first.",
            level=1,
        )

    def play_game(self) -> Player:
        """Play a complete game to 121 points.

        Returns:
            The winning player
        """
        self._log("=" * 60, level=1)
        self._log("STARTING NEW GAME", level=1)
        self._log("=" * 60, level=1)

        while not self.winner:
            self.play_hand()

        self._log("=" * 60, level=1)
        self._log(
            f"GAME OVER! {self.winner.name} wins with {self.winner.score} points!",
            level=1,
        )
        self._log("=" * 60, level=1)

        return self.winner

    def play_hand(self) -> None:
        """Play a complete hand (deal, discard, play, count)."""
        self.hand_number += 1
        self._log(f"\n{'=' * 60}", level=1)
        self._log(f"HAND {self.hand_number}", level=1)
        self._log(f"Dealer: {self.players[self.dealer_idx].name}", level=1)
        self._log(f"{'=' * 60}", level=1)

        # Reset hand state
        self._reset_hand()

        # Deal cards
        self._deal_cards()

        # Discard phase
        self._discard_phase()

        # Cut for starter
        self._cut_starter()

        # Play phase (pegging)
        self._play_phase()

        # Check if game won during play
        if self.winner:
            return

        # Counting phase
        self._counting_phase()

        # Switch dealer
        self.dealer_idx = 1 - self.dealer_idx

    def _reset_hand(self) -> None:
        """Reset state for a new hand."""
        self.deck.reset()
        self.deck.shuffle()
        self.crib.clear()
        self.starter = None
        for player in self.players:
            player.clear_hand()

        # Reset hand tracking
        self.dealt_cards = [[], []]
        self.discarded_cards = [[], []]
        self.his_heels = False

        self._log("Deck shuffled and ready.", level=2)

    def _deal_cards(self) -> None:
        """Deal 6 cards to each player."""
        for _ in range(Rules.INITIAL_HAND_SIZE):
            for idx, player in enumerate(self.players):
                card = self.deck.deal_one()
                player.add_cards_to_hand([card])
                self.dealt_cards[idx].append(card)

        self._log(f"Dealt {Rules.INITIAL_HAND_SIZE} cards to each player.", level=2)
        for player in self.players:
            self._log(f"{player.name} hand: {player.hand}", level=2, debug_only=True)

    def _discard_phase(self) -> None:
        """Each player discards 2 cards to the crib."""
        dealer = self.players[self.dealer_idx]

        self._log("Discard phase...", level=2)

        for idx, player in enumerate(self.players):
            is_dealer = player == dealer
            discards = player.choose_discards(is_dealer)
            player.discard_to_crib(discards)
            self.crib.add_cards(discards)

            # Track discards
            self.discarded_cards[idx] = discards

            self._log(
                f"{player.name} discarded: {', '.join(str(c) for c in discards)}",
                level=2,
                debug_only=True,
            )

        self._log(f"Crib: {self.crib}", level=2, debug_only=True)

    def _cut_starter(self) -> None:
        """Cut the deck for the starter card."""
        self.starter = self.deck.deal_one()
        self._log(f"Starter card: {self.starter}", level=2)

        # Check for his heels (Jack as starter)
        self.his_heels = Rules.check_his_heels(self.starter)
        if self.his_heels:
            dealer = self.players[self.dealer_idx]
            dealer.add_score(2, from_play=True)
            self._log(
                f"His heels! {dealer.name} scores 2 points. ({dealer.name}: {dealer.score})",
                level=1,
            )

            if Rules.is_game_won(dealer.score):
                self.winner = dealer

    def _play_phase(self) -> None:
        """Execute the play phase (pegging to 31)."""
        self._log("\nPlay phase (pegging)...", level=2)

        non_dealer_idx = 1 - self.dealer_idx
        current_player_idx = non_dealer_idx  # Non-dealer plays first

        cards_played: List[Tuple[int, Card]] = []  # (player_idx, card)
        current_count = 0
        consecutive_go_count = 0

        while any(player.has_cards() for player in self.players):
            player = self.players[current_player_idx]

            # Try to play a card
            card = player.choose_play_card(current_count)

            if card is None:
                # Player says "Go"
                self._log(f"{player.name} says Go.", level=2)
                consecutive_go_count += 1

                # If both players say go, award go points
                if consecutive_go_count == 2:
                    # Last player to play gets the go
                    if cards_played:
                        last_player_idx, _ = cards_played[-1]
                        last_player = self.players[last_player_idx]
                        go_points = Rules.get_go_points(True, current_count)
                        last_player.add_score(go_points, from_play=True)
                        reason = "31 for 2" if current_count == 31 else "Go for 1"
                        self._log(
                            f"{last_player.name} scores {go_points} ({reason}). ({last_player.name}: {last_player.score})",
                            level=1,
                        )

                        if Rules.is_game_won(last_player.score):
                            self.winner = last_player
                            return

                    # Reset for next round
                    cards_played = []
                    current_count = 0
                    consecutive_go_count = 0

                    # Next player starts (non-dealer if both still have cards)
                    if self.players[non_dealer_idx].has_cards():
                        current_player_idx = non_dealer_idx
                    else:
                        current_player_idx = self.dealer_idx

                else:
                    # Move to next player
                    current_player_idx = 1 - current_player_idx

            else:
                # Play the card
                player.play_card(card)
                current_count += card.value
                cards_played.append((current_player_idx, card))
                consecutive_go_count = 0

                self._log(
                    f"{player.name} plays {card} (count: {current_count})", level=2
                )

                # Score the play
                cards_in_play = [c for _, c in cards_played]
                points, reasons = Scorer.score_play(cards_in_play, current_player_idx)

                if points > 0:
                    player.add_score(points, from_play=True)
                    reason_str = ", ".join(reasons)
                    self._log(
                        f"{player.name} scores {points} ({reason_str}). ({player.name}: {player.score})",
                        level=1,
                    )

                    if Rules.is_game_won(player.score):
                        self.winner = player
                        return

                # If count is 31, reset
                if current_count == 31:
                    cards_played = []
                    current_count = 0
                    # Next player starts
                    if self.players[non_dealer_idx].has_cards():
                        current_player_idx = non_dealer_idx
                    else:
                        current_player_idx = self.dealer_idx
                else:
                    # Move to next player
                    current_player_idx = 1 - current_player_idx

    def _counting_phase(self) -> None:
        """Count hands and crib."""
        self._log("\nCounting phase...", level=1)

        non_dealer_idx = 1 - self.dealer_idx
        dealer_idx = self.dealer_idx

        # Track scores before counting for hand details export
        p1_score_before = self.players[0].get_score()
        p2_score_before = self.players[1].get_score()

        # Non-dealer counts first
        non_dealer = self.players[non_dealer_idx]
        non_dealer_score, non_dealer_breakdown = Scorer.score_hand(
            non_dealer.get_play_hand(), self.starter, is_crib=False
        )
        self._log_and_score_hand(
            non_dealer,
            non_dealer.get_play_hand(),
            non_dealer_score,
            non_dealer_breakdown,
            is_crib=False,
        )

        if self.winner:
            return

        # Dealer counts hand
        dealer = self.players[dealer_idx]
        dealer_score, dealer_breakdown = Scorer.score_hand(
            dealer.get_play_hand(), self.starter, is_crib=False
        )
        self._log_and_score_hand(
            dealer,
            dealer.get_play_hand(),
            dealer_score,
            dealer_breakdown,
            is_crib=False,
        )

        if self.winner:
            return

        # Dealer counts crib
        crib_score, crib_breakdown = Scorer.score_hand(
            self.crib.get_cards(), self.starter, is_crib=True
        )
        self._log_and_score_hand(
            dealer, self.crib.get_cards(), crib_score, crib_breakdown, is_crib=True
        )

        # Export hand details if exporter configured
        if self.hand_details_exporter:
            # Organize breakdowns by player index (0 or 1)
            if non_dealer_idx == 0:
                p1_breakdown = non_dealer_breakdown
                p2_breakdown = dealer_breakdown
            else:
                p1_breakdown = dealer_breakdown
                p2_breakdown = non_dealer_breakdown

            self._export_hand_details(
                p1_score_before,
                p2_score_before,
                p1_breakdown,
                p2_breakdown,
                crib_breakdown,
            )

    def _log_and_score_hand(
        self,
        player: Player,
        cards: List[Card],
        points: int,
        breakdown: Dict[str, int],
        is_crib: bool = False,
    ) -> None:
        """Log and score a hand or crib.

        Args:
            player: Player whose hand is being counted
            cards: Cards to count
            points: Pre-calculated points
            breakdown: Pre-calculated scoring breakdown
            is_crib: Whether this is the crib
        """
        hand_type = "crib" if is_crib else "hand"
        self._log(
            f"\n{player.name}'s {hand_type}: {', '.join(str(c) for c in cards)}",
            level=1,
        )
        self._log(f"Starter: {self.starter}", level=1)

        if self.verbosity >= 2 or self.debug:
            for category, pts in breakdown.items():
                if pts > 0:
                    self._log(f"  {category}: {pts}", level=2)

        player.add_score(points, from_play=False)
        self._log(
            f"{player.name} scores {points} points. ({player.name}: {player.score})",
            level=1,
        )

        if Rules.is_game_won(player.score):
            self.winner = player

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
            game_number=self.game_number,
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

    def _log(self, message: str, level: int = 1, debug_only: bool = False) -> None:
        """Log a message based on verbosity settings.

        Args:
            message: Message to log
            level: Minimum verbosity level required (0, 1, 2)
            debug_only: Only log if debug mode is enabled
        """
        if debug_only and not self.debug:
            return

        should_log = self.verbosity >= level or self.debug

        if should_log:
            # Print to console
            print(message)

            # Write to log file if configured
            if self.log_file:
                with open(self.log_file, "a") as f:
                    f.write(message + "\n")

    def get_scores(self) -> Dict[str, int]:
        """Get current scores for both players.

        Returns:
            Dict mapping player names to scores
        """
        return {player.name: player.score for player in self.players}

    def get_winner(self) -> Optional[Player]:
        """Get the winner if game is complete.

        Returns:
            Winning player or None if game not finished
        """
        return self.winner
