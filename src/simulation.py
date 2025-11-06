# -----------------------------------------------
# simulation.py — Front-to-Back Boarding Simulation
# -----------------------------------------------
#
# This module implements a discrete-time, single-aisle boarding simulator
# using the Plane and Passenger modules provided in this repo. It follows
# the outline Ali shared (sections 1–8) and is intentionally compact and
# documented so it’s easy to extend for other strategies (WILMA, random,
# back-to-front, etc.).
#
# Quick start
# -----------
#   python simulation.py
#
# You can also import run_once() from notebooks for experiments.
# -----------------------------------------------

# 1) IMPORTS
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

# Local modules
from plane import Plane, defaultArrangement
from passenger import Passenger, generate_passengers


# 2) SIMULATION CONFIGURATION
@dataclass
class SimConfig:
    # Plane settings
    num_rows: int = 30
    seat_arrangement: List[str] = field(default_factory=lambda: list(defaultArrangement))
    bin_capacity_per_row: int = 4

    # Passenger generation
    num_passengers: int = 180
    seat_letters: Optional[List[str]] = None  # defaults to A..F if None
    p_have_bag: float = 0.8
    p_missed: float = 0.02
    walk_mean: float = 1.0
    walk_sd: float = 0.2
    stow_mean: float = 2.0
    stow_sd: float = 0.5

    # Engine / replication
    seed: Optional[int] = 42
    max_ticks: int = 10_000
    collect_time_series: bool = True


# 4) METRICS / TRACKING CLASS
@dataclass
class Metrics:
    total_ticks: int = 0
    seated_count: int = 0
    congestion_ts: List[int] = field(default_factory=list)  # people-in-aisle per tick

    # Per-passenger timestamps
    entry_time: Dict[int, int] = field(default_factory=dict)   # pid -> t when first enters
    seat_time: Dict[int, int] = field(default_factory=dict)    # pid -> t when seated

    def init_for_population(self, passengers: List[Passenger]):
        self.total_ticks = 0
        self.seated_count = 0
        self.congestion_ts.clear()
        self.entry_time.clear()
        self.seat_time.clear()
        for p in passengers:
            # Initialize keys for consistency (optional)
            self.entry_time.setdefault(p.pid, None)  # type: ignore
            self.seat_time.setdefault(p.pid, None)   # type: ignore

    def record_congestion(self, plane: Plane):
        # Count everyone currently occupying an aisle cell (including entrance index 0)
        self.congestion_ts.append(sum(1 for cell in plane.aisle if cell is not None))


# 3) QUEUE GENERATION STRATEGY (front-to-back)

def build_front_to_back_queue(passengers: List[Passenger]) -> List[Passenger]:
    """Sort passengers in ascending target_row (1 → N).
    Preserve random order among same-row passengers to avoid bias.
    """
    # Group by row
    by_row: Dict[int, List[Passenger]] = {}
    for p in passengers:
        by_row.setdefault(p.target_row, []).append(p)
    # Shuffle within each row group, then concatenate by ascending row
    ordered: List[Passenger] = []
    for r in sorted(by_row.keys()):
        group = by_row[r]
        random.shuffle(group)
        ordered.extend(group)
    return ordered


# 5) SIMULATION HELPERS

def _ensure_seat_passenger_method(plane: Plane) -> None:
    """Compatibility: passenger.step() expects plane.seat_passenger().
    Our Plane class exposes Plane.occupy(). If seat_passenger is missing,
    add a thin adapter method at runtime.
    """
    if not hasattr(plane, "seat_passenger"):
        def seat_passenger(row: int, letter: str) -> bool:  # type: ignore
            return plane.occupy(row, letter)
        setattr(plane, "seat_passenger", seat_passenger)


def inject_next_if_possible(queue: List[Passenger], plane: Plane, t: int, m: Metrics):
    """Allow the next passenger to attempt entrance this tick.
    We only let the queue[0] try to step; their step() will enter
    if the entrance cell (aisle[0]) is free. If they do enter, record entry time
    and remove them from the queue.
    """
    if not queue:
        return
    nxt = queue[0]
    pre_pos = nxt.aisle_pos
    nxt.step(plane)
    if pre_pos == -1 and nxt.aisle_pos == 0:
        # First time entering
        if m.entry_time.get(nxt.pid) is None:
            m.entry_time[nxt.pid] = t
        queue.pop(0)


def step_all_passengers(passengers: List[Passenger], plane: Plane, t: int, m: Metrics):
    """Advance all passengers one time step.
    To avoid overwriting moves, iterate aisle cells from back to front and call
    step() on the occupant, then handle newly seated timestamps.
    """
    # Process aisle occupants from farthest back toward the entrance
    for idx in range(len(plane.aisle) - 1, -1, -1):
        person = plane.aisle[idx]
        if isinstance(person, Passenger):
            before_seated = person.seated
            person.step(plane)
            if not before_seated and person.seated:
                # Seated this tick — record seat time
                if m.seat_time.get(person.pid) is None:
                    m.seat_time[person.pid] = t
                m.seated_count += 1


def everyone_seated(passengers: List[Passenger]) -> bool:
    return all(p.seated or p.missed for p in passengers)


# 6) MAIN SIMULATION LOOP

def run_once(cfg: SimConfig) -> Tuple[Metrics, Plane, List[Passenger]]:
    if cfg.seed is not None:
        random.seed(cfg.seed)

    # Build plane
    plane = Plane(
        num_rows=cfg.num_rows,
        arrangement=cfg.seat_arrangement,
        bin_capacity_per_row=cfg.bin_capacity_per_row,
    ).generate_plane()
    _ensure_seat_passenger_method(plane)

    # Generate passengers and strategy queue
    passengers = generate_passengers(
        num_passengers=cfg.num_passengers,
        num_rows=cfg.num_rows,
        seat_letters=cfg.seat_letters,
        p_have_bag=cfg.p_have_bag,
        p_missed=cfg.p_missed,
        walk_mean=cfg.walk_mean,
        walk_sd=cfg.walk_sd,
        stow_mean=cfg.stow_mean,
        stow_sd=cfg.stow_sd,
    )
    queue = build_front_to_back_queue(passengers)

    # Metrics
    m = Metrics()
    m.init_for_population(passengers)

    # Discrete-time loop
    for t in range(cfg.max_ticks):
        # 1) Inject next in line if entrance is free (via their step)
        inject_next_if_possible(queue, plane, t, m)

        # 2) Move everyone already on board
        step_all_passengers(passengers, plane, t, m)

        # 3) Record congestion (optional)
        if cfg.collect_time_series:
            m.record_congestion(plane)

        # 4) Stop condition
        if everyone_seated(passengers):
            m.total_ticks = t + 1  # ticks are 0-indexed, so add 1
            break
    else:
        # max_ticks exhausted
        m.total_ticks = cfg.max_ticks

    return m, plane, passengers


# 7) METRIC SUMMARIZATION

def summarize(m: Metrics) -> Dict[str, float]:
    seated_times = [t for t in m.seat_time.values() if t is not None]
    avg_time_to_seat = (sum(seated_times) / len(seated_times)) if seated_times else float("nan")
    max_congestion = max(m.congestion_ts) if m.congestion_ts else 0
    return {
        "total_boarding_ticks": float(m.total_ticks),
        "seated_count": float(m.seated_count),
        "avg_time_to_seat_ticks": float(avg_time_to_seat),
        "max_congestion": float(max_congestion),
    }


# 8) MAIN SCRIPT EXECUTION
if __name__ == "__main__":
    cfg = SimConfig(
        num_rows=30,
        seat_arrangement=list(defaultArrangement),
        bin_capacity_per_row=4,
        num_passengers=180,
        seed=42,
        max_ticks=20_000,
        collect_time_series=True,
    )
    metrics, plane, passengers = run_once(cfg)

    stats = summarize(metrics)
    print("\nFront-to-Back Boarding — Single Run Summary")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Optional quick visualization in console
    # plane.show_plane(mode="status")  # uncomment to see final layout
