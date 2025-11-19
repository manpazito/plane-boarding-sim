"""
Custom Boarding Strategy Template

How to use this file
--------------------

1. COPY THIS FILE and rename it to something like:
       src/custom_strategies/my_even_odd_strategy.py

2. In your copy:
   - Change STRATEGY_NAME to a short, unique id (no spaces).
   - Rename CustomBoardingStrategy to something meaningful.
   - Replace the example logic in __call__ with your own algorithm.

3. Run the simulator with:
       python src/simulation.py --strategy my_even_odd

   The simulator will:
   - generate passengers
   - call your strategy(passengers) to build the queue
   - run the boarding simulation and write metrics + GIFs
"""

from typing import List
import random

from passenger import Passenger
from basic_strategies import BoardingStrategy, STRATEGIES


# Change this to a unique, short ID (no spaces)
STRATEGY_NAME = "my_custom_strategy"


class CustomBoardingStrategy(BoardingStrategy):
    """
    Example custom boarding strategy.

    Requirements:
    -------------
    - Implement __call__(self, passengers: List[Passenger]) -> List[Passenger]
    - Return a NEW list with the same Passenger objects, in the order you want
      them to line up outside the plane.
    - DO NOT create or delete passengers; just reorder them.
    """

    name: str = STRATEGY_NAME

    def __call__(self, passengers: List[Passenger]) -> List[Passenger]:
        """
        Reorder the passenger list to define your boarding queue.

        Arguments
        ---------
        passengers : list[Passenger]
            All passengers on this flight. Each Passenger has:
            - target_row (int, 1-based)
            - target_letter (str, e.g., 'A'..'F')

        Returns
        -------
        ordered_passengers : list[Passenger]
            Same passengers, new order.
        """

        # -------- EXAMPLE STRATEGY (replace this with your own) --------
        # Example: even-numbered rows first, then odd-numbered rows.
        even_rows = [p for p in passengers if p.target_row % 2 == 0]
        odd_rows = [p for p in passengers if p.target_row % 2 == 1]

        random.shuffle(even_rows)
        random.shuffle(odd_rows)

        ordered_passengers = even_rows + odd_rows
        # -------- END EXAMPLE --------

        # Safety checks: good practice while developing your strategy
        assert len(ordered_passengers) == len(
            passengers
        ), "Custom strategy changed number of passengers!"
        assert set(ordered_passengers) == set(
            passengers
        ), "Custom strategy must return the SAME Passenger objects, just reordered."

        return ordered_passengers


# Register strategy so the simulator can find it by name.
STRATEGIES[STRATEGY_NAME] = CustomBoardingStrategy()
