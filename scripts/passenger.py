import random
import math

# NOTES / TODOs FOR FUTURE PARAMETER RESEARCH
# ------------------------------------------------------------------
# This file contains simple placeholder parameters and sampling rules for
# passenger behavior (carry-on probability, no-shows, walking cadence, stow
# times). Before using simulation outputs for any real-world decision-making
# we should replace these with empirically grounded distributions. Add
# or update the items below as research is completed.
#
# Parameters to investigate (in-code reference)
# - p_have_bag: probability a passenger carries a suitcase onto the plane.
#   * Current placeholder: 0.8
#   * Why: strongly affects aisle blocking and overhead bin congestion.
#   * Suggested data sources: airline baggage reports, gate observations.
#   * Suggested modeling: conditional probability by fare class, route,
#     time-of-day. Consider bag-size categories (small/med/large) with
#     volume-based bin filling.
#   * Tentative ranges: 0.5 - 0.95
#
# - p_missed: no-show probability
#   * Current placeholder: 0.02
#   * Why: impacts realized passenger counts and boarding throughput.
#   * Data sources: airline load factors / no-show reports.
#   * Tentative ranges: 0.005 - 0.05
#
# - walk_ticks / walking speed
#   * Current placeholder: Normal(mean=1.0, sd=0.2) floored to >=1 ticks
#   * Why: controls how quickly passengers move along the aisle.
#   * Data sources: video time-motion studies, published pedestrian dynamics.
#   * Suggested modeling: measure speed in m/s and convert rows-per-tick using
#     physical row spacing + tick duration. Replace normal with log-normal or
#     gamma if distribution is right-skewed. Consider covariates (age,
#     mobility aid, group size, carry-ons).
#
# - stow_ticks / stow time
#   * Current placeholder: Normal(mean=2.0, sd=0.5) ticks (or sampled fallback)
#   * Why: major contributor to aisle blocking at seat rows.
#   * Data sources: timed observations of overhead stow events.
#   * Suggested modeling: mixture model by bag size and passenger familiarity;
#     some stows quick (<=1 tick), some long (>5 ticks).
#
# - overhead_bins (capacity per row)
#   * Current placeholder: fixed integer count per row (default 4)
#   * Why: determines how often bins fill; a more realistic model would use
#     bin volume and bag volumes.
#   * Data sources: aircraft bin specs, measured bag volumes.
#
# Modeling recommendations
# - Prefer positive-only distributions (log-normal/gamma) for timing data.
# - Add passenger covariates (age, fare class, group size) to explain heterogeneity.
# - Consider a pre-boarding queue model (multiple slots outside the aircraft)
#   instead of a single `aisle[0]` slot.
# - For sensitivity analysis, run broad sweeps across carry-on rate, stow mean,
#   and walking-speed parameters; use Latin Hypercube Sampling for efficiency.
#
# Keep this comment up-to-date: as research adds parameter estimates, replace
# placeholders and move details into small data fixtures or config files.


class Passenger:
    def __init__(self, pid, target_row, target_letter,
                 has_bag=None, missed=False, walk_ticks=1, stow_ticks=None):
        self.pid = pid
        self.target_row = target_row          # 1-based row number
        self.target_letter = target_letter    # 'A', 'B', etc.

        self.aisle_pos = -1                   # -1 = not yet entered plane
        self.seated = False

        # attendance
        self.missed = bool(missed)

        # overhead bin behavior
        self.has_bag = (has_bag if has_bag is not None else (random.random() < 0.8))
        self.active_delay = 0                 # how many ticks I'm currently blocking aisle
        self.done_stowing = False             # did I already put my bag up?

        # walking/stow timing (discrete ticks)
        self.walk_ticks = max(1, int(walk_ticks))
        self.walk_timer = 0                   # counts down between allowed steps
        # how many ticks stowing typically takes (None if no bag)
        self.stow_ticks = (None if not self.has_bag else
                           (None if stow_ticks is None else int(max(0, stow_ticks))))

    def step(self, plane):
        # already seated, nothing to do
        
        if self.seated:
            return

        # haven't entered the plane yet: try to step into row 1 aisle (index 0)
        if self.aisle_pos == -1:
            if plane.aisle[0] is None:
                self.aisle_pos = 0
                plane.aisle[0] = self
            return

        dest_idx = self.target_row  # convert seat row to aisle index (entrance is index 0)

        # If I'm still walking to my row
        if self.aisle_pos < dest_idx:
            next_idx = self.aisle_pos + 1
            if plane.aisle[next_idx] is None:
                # enforce walking cadence: only move when walk_timer == 0
                if self.walk_timer > 0:
                    self.walk_timer -= 1
                    return
                # move forward
                plane.aisle[self.aisle_pos] = None
                self.aisle_pos = next_idx
                plane.aisle[self.aisle_pos] = self
                # reset walk timer (ticks between moves)
                self.walk_timer = max(0, self.walk_ticks - 1)
            return

        # I am now at my row
        if self.aisle_pos == dest_idx:
            # If I'm currently stowing or otherwise blocking, count down
            if self.active_delay > 0:
                self.active_delay -= 1
                return

            # Haven't stowed yet and I have a bag → try stowing
            if self.has_bag and not self.done_stowing:
                if plane.try_stow_bag(self.target_row):
                    # Bin had space, stow takes stow_ticks if provided else small random
                    if self.stow_ticks is not None:
                        self.active_delay = int(self.stow_ticks)
                    else:
                        self.active_delay = max(1, int(round(random.gauss(2, 0.5))))
                    self.done_stowing = True
                    return
                else:
                    # Bin ABOVE my row is full. Spend extra time figuring it out.
                    self.active_delay = max(1, int(round(random.gauss(4, 1.0))))
                    self.done_stowing = True  # after this delay, assume it's handled
                    return

            # Either no bag OR bag is already stowed → sit down
            plane.aisle[self.aisle_pos] = None
            plane.seat_passenger(self.target_row, self.target_letter)
            self.seated = True
            return


def generate_passengers(num_passengers, num_rows, seat_letters=None,
                        p_have_bag=0.8, p_missed=0.02,
                        walk_mean=1.0, walk_sd=0.2,
                        stow_mean=2.0, stow_sd=0.5):
    """
    Generate a list of Passenger instances with basic stochastic attributes.

    - num_passengers: desired number of passengers (no-shows removed)
    - num_rows: number of rows on the plane (used to pick seat rows)
    - seat_letters: iterable of seat letters (defaults to A-F)
    - p_have_bag: probability a passenger has a carry-on
    - p_missed: probability a passenger is a no-show (these are skipped)
    - walk_mean, walk_sd: normal params for walking cadence (ticks per step)
    - stow_mean, stow_sd: normal params for stow time in ticks

    Returns: list of Passenger objects (length <= num_passengers)
    """
    # FUTURE WORK / NOTES:
    # - The default probabilities and timing parameters here are placeholders.
    #   Once empirical research is done they should be replaced with realistic
    #   distributions. See `reports/parameter_notes.md` for suggested items to
    #   research (carry-on frequency, no-show rates, walking speed distributions,
    #   stow times by luggage size, demographic effects, ...) and suggested
    #   distributions/ranges.
    # - Consider switching from simple normal sampling to log-normal or gamma
    #   for strictly positive timings (walk cadence, stow time) if data shows
    #   right-skew. Also consider per-passenger covariates (age, group size,
    #   ticket class) that affect parameters.

    if seat_letters is None:
        seat_letters = ["A", "B", "C", "D", "E", "F"]

    # Build pool of available seats
    seats = [(r, l) for r in range(1, num_rows + 1) for l in seat_letters]
    total_seats = len(seats)
    if num_passengers > total_seats:
        # cap to plane capacity
        num_passengers = total_seats

    chosen = random.sample(seats, k=num_passengers)
    passengers = []
    pid = 1
    missed_count = 0
    for (r, l) in chosen:
        if random.random() < p_missed:
            missed_count += 1
            continue

        # walking cadence: ticks per step, sampled from normal and floored to >=1
        walk_ticks = max(1, int(round(random.gauss(walk_mean, walk_sd))))
        # stow ticks if they have a bag
        has_bag = random.random() < p_have_bag
        stow_ticks = None
        if has_bag:
            stow_ticks = max(1, int(round(random.gauss(stow_mean, stow_sd))))

        p = Passenger(pid, r, l, has_bag=has_bag, missed=False,
                      walk_ticks=walk_ticks, stow_ticks=stow_ticks)
        passengers.append(p)
        pid += 1

    # Optionally return stats or just the list
    return passengers