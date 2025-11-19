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
    name = "steffen"

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        by_row = _group_by_row(passengers)
        ordered: List[Passenger] = []
        # Even rows first, then odd rows
        even_rows = sorted([r for r in by_row.keys() if r % 2 == 0])
        odd_rows = sorted([r for r in by_row.keys() if r % 2 != 0])
        for r in even_rows + odd_rows:
            group = list(by_row[r])
            # Sort by seat letter to board window to aisle
            group.sort(key=lambda p: p.target_letter)
            ordered.extend(group)
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
