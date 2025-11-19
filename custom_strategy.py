"""
Custom Boarding Strategy Template

How to use this file
--------------------

1. COPY THIS FILE and rename it to something like:
     my_even_odd_strategy.py
   Do NOT edit the original template if you want to keep a clean example.

2. Change:
     - STRATEGY_NAME
     - The class name (CustomBoardingStrategy -> SomethingMeaningful)
     - The implementation of the __call__ method.

3. Make sure this file is IMPORTED somewhere before running the simulation,
   so that the strategy gets registered. For example, in `simulation.py`:

     from basic_strategies import STRATEGIES
     import custom_strategies.my_even_odd_strategy  # noqa: F401

4. Run the simulator, choosing your strategy by name, e.g.:

     python simulation.py --strategy my_even_odd --runs 20
"""

from typing import List
import random

from src.passenger import Passenger  # adjust import if your path is different
from src.basic_strategies import BoardingStrategy, STRATEGIES


# TODO: change this to a short, unique ID (no spaces)
STRATEGY_NAME = "my_custom_strategy"


class CustomBoardingStrategy(BoardingStrategy):
    """
    Example custom boarding strategy.

    You MUST:
    - Set `name` to STRATEGY_NAME (or another unique string).
    - Implement the `__call__` method to return a NEW list of passengers
      in the order they should enter the plane.

    The simulator expects:
        strategy(passengers: List[Passenger]) -> List[Passenger]

    - `passengers` contains ALL passengers generated for this run.
      Each Passenger has at least:
        - target_row (int, 0-indexed; row 0 is front or back depending on your config)
        - target_letter (str, e.g., "A", "B", ..., "F")

    - You must return a list that:
        * Contains exactly the same Passenger objects (no duplicates, no missing).
        * Is ordered in the exact queue order you want to test.
    """

    # This is the name the simulator will use on the command line.
    name: str = STRATEGY_NAME

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        """
        Reorder the passenger list to define your boarding queue.

        Arguments
        ---------
        passengers : list of Passenger
            All passengers on this flight, in arbitrary order.

        Returns
        -------
        ordered_passengers : list of Passenger
            The same passengers, in the order you want them to board.

        TEMPLATE EXAMPLE:
        -----------------
        Below is a very simple "even rows first, then odd rows" example.
        Replace this logic with your own algorithm.
        """

        # ---- START OF EXAMPLE LOGIC (you should TOSS or EDIT this) ----

        # Split passengers by even/odd row
        even_rows = [p for p in passengers if p.target_row % 2 == 0]
        odd_rows = [p for p in passengers if p.target_row % 2 == 1]

        # Within each group, shuffle so it isn't totally deterministic
        random.shuffle(even_rows)
        random.shuffle(odd_rows)

        ordered_passengers = even_rows + odd_rows

        # ---- END OF EXAMPLE LOGIC ----

        # Safety check (good debugging aid): ensure we didn't lose or duplicate anyone
        assert len(ordered_passengers) == len(
            passengers
        ), "Custom strategy changed number of passengers!"
        assert set(ordered_passengers) == set(
            passengers
        ), "Custom strategy must return same passengers!"

        return ordered_passengers


# IMPORTANT: register this strategy so the simulator can find it
# The global STRATEGIES dict is used by `simulation.py` to list strategies.
STRATEGIES[STRATEGY_NAME] = CustomBoardingStrategy()
