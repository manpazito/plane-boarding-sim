"""Basic boarding strategy helpers implemented as classes.

This module is a direct copy of the previous `strategies.py` module and
provides a small set of named strategy instances suitable for experiments
and examples (back_to_front, front_to_back, random, wilma, grouped).

Each strategy is a callable class instance (implements __call__) and
exposes a human-friendly `name` attribute.
"""

from typing import List, Callable, Tuple
import random

# Import Passenger (kept at module-level for type clarity)
from passenger import Passenger


def _group_by_row(passengers: List[Passenger]):
    by_row = {}
    for p in passengers:
        by_row.setdefault(p.target_row, []).append(p)
    return by_row


class BoardingStrategy:
    """Base class for boarding strategies.

    Subclasses should implement `def __call__(self, passengers: List[Passenger]) -> List[Passenger]`.
    """

    name: str = "base_strategy"

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        raise NotImplementedError()

    def __repr__(self):
        return f"<BoardingStrategy {self.name}>"


class FrontToBack(BoardingStrategy):
    name = "front_to_back"

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        by_row = _group_by_row(passengers)
        ordered: List[Passenger] = []
        for r in sorted(by_row.keys()):
            group = list(by_row[r])
            random.shuffle(group)
            ordered.extend(group)
        return ordered


class BackToFront(BoardingStrategy):
    name = "back_to_front"

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        by_row = _group_by_row(passengers)
        ordered: List[Passenger] = []
        for r in sorted(by_row.keys(), reverse=True):
            group = list(by_row[r])
            random.shuffle(group)
            ordered.extend(group)
        return ordered


class RandomOrder(BoardingStrategy):
    name = "random"

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        out = list(passengers)
        random.shuffle(out)
        return out


class Wilma(BoardingStrategy):
    name = "wilma"

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        # Detect common A-F set
        letters = {p.target_letter for p in passengers}
        expected = {"A", "B", "C", "D", "E", "F"}
        if not expected.issubset(letters):
            # Fallback for non-standard layouts
            return RandomOrder()(passengers)

        # Define groups in WILMA order
        window = {"A", "F"}
        middle = {"B", "E"}
        aisle = {"C", "D"}

        by_row = _group_by_row(passengers)
        ordered: List[Passenger] = []
        for r in sorted(by_row.keys(), reverse=True):
            group = by_row[r]
            row_window = [p for p in group if p.target_letter in window]
            row_middle = [p for p in group if p.target_letter in middle]
            row_aisle = [p for p in group if p.target_letter in aisle]
            random.shuffle(row_window)
            random.shuffle(row_middle)
            random.shuffle(row_aisle)
            ordered.extend(row_window + row_middle + row_aisle)
        return ordered


class Steffen(BoardingStrategy):
    """
    Approximate implementation of the Steffen (2017) boarding method
    for a 6-across single-aisle cabin (seats A–F).

    Order:
      1) Window seats (A,F) from back, every other row, then the offset rows
      2) Middle seats (B,E) with the same pattern
      3) Aisle seats (C,D) with the same pattern
    """

    name = "steffen"

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        # If the seat layout isn't A–F, fall back to random
        letters = {p.target_letter for p in passengers}
        expected = {"A", "B", "C", "D", "E", "F"}
        if not expected.issubset(letters):
            return RandomOrder()(passengers)

        by_row = _group_by_row(passengers)

        # Back row index:
        max_row = max(by_row.keys())

        # Seat groups in Steffen order: windows, middle, aisle
        seat_groups = [
            {"A", "F"},  # windows
            {"B", "E"},  # middle
            {"C", "D"},  # aisle
        ]

        ordered: List[Passenger] = []

        for group_letters in seat_groups:
            # First wave: rows with same parity as max_row (max, max-2, ...)
            for start in (max_row, max_row - 1):
                if start <= 0:
                    continue
                for r in range(start, 0, -2):
                    if r not in by_row:
                        continue

                    # Take only seats in this seat-group for this row
                    row_group = [
                        p for p in by_row[r] if p.target_letter in group_letters
                    ]

                    # Within row+group, board in a fixed left-to-right order
                    row_group.sort(key=lambda p: p.target_letter)
                    ordered.extend(row_group)

        # Safety: if anything was missed (weird seats, etc.), append in original order
        remaining = [p for p in passengers if p not in ordered]
        ordered.extend(remaining)

        return ordered


class GroupedBoarding(BoardingStrategy):
    """Boards rows in the specified groups.

    groups: list of (start_row, end_row) inclusive ranges. Rows inside a
    group are shuffled.
    """

    def __init__(self, groups: List[Tuple[int, int]]):
        self.groups = list(groups)
        self.name = f"grouped_{'_'.join(f'{a}-{b}' for (a,b) in groups)}"

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        by_row = _group_by_row(passengers)
        ordered: List[Passenger] = []
        for start, end in self.groups:
            rows = [r for r in sorted(by_row.keys()) if start <= r <= end]
            for r in rows:
                group = list(by_row[r])
                random.shuffle(group)
                ordered.extend(group)
        remaining = [
            r
            for r in sorted(by_row.keys())
            if not any(start <= r <= end for (start, end) in self.groups)
        ]
        for r in remaining:
            group = list(by_row[r])
            random.shuffle(group)
            ordered.extend(group)
        return ordered


# Export default instances for convenience (backwards-compatible names)
front_to_back = FrontToBack()
back_to_front = BackToFront()
random_order = RandomOrder()
wilma = Wilma()
steffen = Steffen()


def register_strategy(strategy: BoardingStrategy):
    """Helper so users can easily register custom strategies."""
    STRATEGIES[strategy.name] = strategy


# Export a dictionary of strategies for convenience
STRATEGIES = {
    "front_to_back": front_to_back,
    "back_to_front": back_to_front,
    "random": random_order,
    "wilma": wilma,
    "steffen": steffen,
}
