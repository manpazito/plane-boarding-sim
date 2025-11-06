# -----------------------------------------------
# simulation.py — Front-to-Back Boarding Simulation
# -----------------------------------------------
# LLM Conversation Link: https://chatgpt.com/share/690c27a7-e63c-8009-b2bc-58adb234f21b
#
# File Generated Based on the following Outline:
#
# -----------------------------------------------
# simulation.py — Outline for Front-to-Back Boarding Simulation
# -----------------------------------------------

# 1. IMPORTS
# Import necessary modules:
# - random for stochastic behavior
# - dataclasses for config storage
# - typing for type hints
# - Plane and Passenger modules to build the environment and agents

# 2. SIMULATION CONFIGURATION
# Define a @dataclass 'SimConfig' to hold all simulation parameters:
# - plane settings (num_rows, bin capacity, seat arrangement)
# - passenger behavior parameters (probabilities, timing)
# - random seed and simulation limits (ticks, time series collection)

# 3. QUEUE GENERATION STRATEGY
# Define a function 'build_front_to_back_queue(passengers)' that:
# - sorts passengers by ascending target_row (1 → N)
# - keeps same-row passengers in random order
# - returns a queue list to represent boarding order

# 4. METRICS / TRACKING CLASS
# Create a @dataclass 'Metrics' to store:
# - total boarding ticks
# - number of seated passengers
# - per-tick congestion (number of people in aisle)
# - per-passenger entry and seat timestamps
# Include helper methods:
# - 'init_for_population()' to prepare data structures
# - 'record_congestion()' to log number of active passengers per tick

# 5. SIMULATION HELPERS
# Define helper functions for each time-step operation:
# - 'inject_next_if_possible()': let the next passenger enter the plane
# - 'step_all_passengers()': move each passenger forward one step per tick
#   (loop from back to front so movements don't overwrite aisle positions)
# - 'everyone_seated()': check if all passengers have reached their seats

# 6. MAIN SIMULATION LOOP
# Define 'run_once(cfg: SimConfig)' that executes one full simulation run:
# - set random seed
# - create Plane instance and generate its structure (aisle, seats, bins)
# - generate passengers via 'generate_passengers()'
# - sort passengers using front-to-back queue
# - initialize metrics
# - run discrete-event loop (for t in range(max_ticks)):
#     1) inject next passenger if entrance open
#     2) call step() on each active passenger
#     3) record congestion metrics
#     4) check stop condition (all seated)
# - return metrics, plane, passengers at end

# 7. METRIC SUMMARIZATION
# Write a 'summarize(metrics)' function that computes key statistics:
# - total boarding time
# - average time to seat
# - maximum congestion
# - optionally export to a dict for plotting or analysis

# 8. MAIN SCRIPT EXECUTION
# Include a '__main__' guard to:
# - initialize default config (e.g., 30 rows, 180 passengers)
# - run one simulation with 'run_once(cfg)'
# - print results using 'summarize()'
# - optionally visualize final plane seating layout

# -----------------------------------------------
# END OF FILE
# -----------------------------------------------

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
from typing import List, Dict, Tuple, Optional, Callable
import time
import os
import io
from contextlib import redirect_stdout

# Local modules
from plane import Plane, defaultArrangement
from passenger import Passenger, generate_passengers
from basic_strategies import back_to_front

# GIF maker (import from sibling module in src/)
try:
    from make_gif_from_text_frames import make_gif
except Exception:
    # If import fails (different execution context), we'll call it dynamically later.
    make_gif = None


# 2) SIMULATION CONFIGURATION
@dataclass
class SimConfig:
    # Plane settings
    num_rows: int = 30
    seat_arrangement: List[str] = field(
        default_factory=lambda: list(defaultArrangement)
    )
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
    # When True, if the run is asked to generate exactly the number of
    # available seats, we will force p_missed to 0.0 so no-shows do not
    # reduce the passenger count (useful for basic "full plane" experiments).
    disable_no_shows_when_filling: bool = True


# 4) METRICS / TRACKING CLASS
@dataclass
class Metrics:
    total_ticks: int = 0
    seated_count: int = 0
    congestion_ts: List[int] = field(default_factory=list)  # people-in-aisle per tick

    # Per-passenger timestamps
    entry_time: Dict[int, int] = field(
        default_factory=dict
    )  # pid -> t when first enters
    seat_time: Dict[int, int] = field(default_factory=dict)  # pid -> t when seated

    def init_for_population(self, passengers: List[Passenger]):
        self.total_ticks = 0
        self.seated_count = 0
        self.congestion_ts.clear()
        self.entry_time.clear()
        self.seat_time.clear()
        for p in passengers:
            # Initialize keys for consistency (optional)
            self.entry_time.setdefault(p.pid, None)  # type: ignore
            self.seat_time.setdefault(p.pid, None)  # type: ignore

    def record_congestion(self, plane: Plane):
        # Count everyone currently occupying an aisle cell (including entrance index 0)
        self.congestion_ts.append(sum(1 for cell in plane.aisle if cell is not None))


# 3) QUEUE GENERATION STRATEGY (front-to-back)

# Queue-building strategies are implemented in `src/basic_strategies.py`.
# We import the desired strategy (back_to_front) and use it as the default
# in run_once(). If you need front-to-back or others, import them from
# `basic_strategies` and pass as `boarding_strategy` to run_once().

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


def run_once(
    cfg: SimConfig,
    boarding_strategy: Optional[Callable[[List[Passenger]], List[Passenger]]] = None,
    animate: bool = False,
    frame_delay: float = 0.05,
    save_frames: bool = False,
    frames_dir: Optional[str] = None,
    perfect_queue: bool = True,
    auto_make_gif: bool = False,
    gif_duration: int = 150,
    gif_font: Optional[str] = None,
    gif_font_size: int = 16,
    gif_scale: int = 2,
) -> Tuple[Metrics, Plane, List[Passenger]]:
    if cfg.seed is not None:
        random.seed(cfg.seed)

    # Build plane
    plane = Plane(
        num_rows=cfg.num_rows,
        arrangement=cfg.seat_arrangement,
        bin_capacity_per_row=cfg.bin_capacity_per_row,
    ).generate_plane()
    _ensure_seat_passenger_method(plane)

    # Generate passengers
    # Decide number of passengers to generate. By default cap at available seats
    total_seats = len([s for s in plane.seat_map.values() if not s.occupied])
    # If user-provided cfg.num_passengers is <= 0 or larger than available seats,
    # use the available seats so the basic full-plane case is supported.
    if cfg.num_passengers is None or cfg.num_passengers <= 0:
        num_to_create = total_seats
    else:
        num_to_create = min(cfg.num_passengers, total_seats)

    if num_to_create != cfg.num_passengers:
        print(
            f"Adjusting num_passengers -> {num_to_create} (available seats: {total_seats})"
        )

    # If we're filling the plane (num_to_create == total_seats) we may
    # optionally disable no-shows so the generated passenger count equals
    # the available seats. This behavior is controlled by
    # cfg.disable_no_shows_when_filling.
    if num_to_create == total_seats and cfg.disable_no_shows_when_filling:
        p_missed_for_gen = 0.0
    else:
        p_missed_for_gen = cfg.p_missed

    passengers = generate_passengers(
        num_passengers=num_to_create,
        num_rows=cfg.num_rows,
        seat_letters=cfg.seat_letters,
        p_have_bag=cfg.p_have_bag,
        p_missed=p_missed_for_gen,
        walk_mean=cfg.walk_mean,
        walk_sd=cfg.walk_sd,
        stow_mean=cfg.stow_mean,
        stow_sd=cfg.stow_sd,
    )
    # Decide boarding strategy: use provided function or default to back-to-front
    strategy = boarding_strategy or back_to_front
    queue = strategy(passengers)

    # Human-friendly strategy name used for filenames and reporting
    try:
        if hasattr(strategy, "name") and getattr(strategy, "name"):
            sname = getattr(strategy, "name")
        elif hasattr(strategy, "__name__") and getattr(strategy, "__name__"):
            sname = getattr(strategy, "__name__")
        elif hasattr(strategy, "__class__") and hasattr(strategy.__class__, "__name__"):
            sname = strategy.__class__.__name__
        else:
            sname = "strategy"
    except Exception:
        sname = "strategy"

    # Create a per-run directory under results/ to store frames, GIF and CSV.
    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    run_id = int(time.time())
    # If caller supplied a frames_dir, we'll still create a run directory under
    # results/ to keep outputs organized consistently.
    run_dir = os.path.join(repo_root, "results", f"{sname}_{run_id}")
    os.makedirs(run_dir, exist_ok=True)
    # Default frames_dir becomes a subdirectory inside run_dir
    if frames_dir is None:
        frames_dir = os.path.join(run_dir, f"{sname}_animation_frames")
    else:
        # Normalize provided path but place frames inside the run_dir to keep
        # structure consistent.
        frames_dir = os.path.join(run_dir, f"{sname}_animation_frames")
    # Ensure frames directory exists when needed (created on-demand in loop)
    # but create it now so downstream code can rely on its existence.
    if save_frames:
        os.makedirs(frames_dir, exist_ok=True)

    # If the experiment assumes passengers are perfectly lined up by grouping,
    # enforce a deterministic order within groups so boarding visuals match the
    # strategy exactly (no intra-group randomization).
    if perfect_queue:

        def _deterministic_order(q: List[Passenger]) -> List[Passenger]:
            # Prefer simple heuristics based on strategy name
            name = getattr(strategy, "__name__", "") or ""
            # Back-to-front: rows descending, then seat letter
            if "back" in name:
                return sorted(q, key=lambda p: (-p.target_row, p.target_letter))
            # Front-to-back: rows ascending
            if "front" in name:
                return sorted(q, key=lambda p: (p.target_row, p.target_letter))
            # WILMA: deterministic window->middle->aisle order, rows back->front
            if "wilma" in name:
                window = {"A", "F"}
                middle = {"B", "E"}
                aisle = {"C", "D"}

                def seat_group(letter: str):
                    if letter in window:
                        return 0
                    if letter in middle:
                        return 1
                    return 2

                return sorted(
                    q,
                    key=lambda p: (
                        -p.target_row,
                        seat_group(p.target_letter),
                        p.target_letter,
                    ),
                )
            # General fallback: preserve the row ordering implied by `q` but
            # make intra-row ordering deterministic by seat letter
            row_order = list(dict.fromkeys([p.target_row for p in q]))
            out: List[Passenger] = []
            for r in row_order:
                row_group = [p for p in q if p.target_row == r]
                out.extend(sorted(row_group, key=lambda p: p.target_letter))
            return out

        queue = _deterministic_order(queue)
        # Also reorder the main passengers list to reflect the lined-up queue
        # (not strictly necessary but keeps logs consistent)
        passengers = list(queue)

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

        # Optional simple console animation and/or frame saving
        if animate or save_frames:
            # Capture the plane snapshot as a string
            buf = io.StringIO()
            with redirect_stdout(buf):
                print(f"Tick: {t}   queue_len: {len(queue)}   seated: {m.seated_count}")
                plane.show_plane(mode="status")
            snapshot = buf.getvalue()

            if animate:
                # Clear terminal and print snapshot
                print("\033[H\033[J", end="")
                print(snapshot)
                time.sleep(frame_delay)

            if save_frames:
                # frames_dir was prepared earlier to point inside the per-run folder
                os.makedirs(frames_dir, exist_ok=True)
                fname = os.path.join(frames_dir, f"{sname}_frame_{t:05d}.txt")
                with open(fname, "w", encoding="utf-8") as fh:
                    fh.write(snapshot)

        # 4) Stop condition
        if everyone_seated(passengers):
            m.total_ticks = t + 1  # ticks are 0-indexed, so add 1
            break
    else:
        # max_ticks exhausted
        m.total_ticks = cfg.max_ticks

    # After the run, write summary metrics CSV into results/metrics
    # Prefer a human-friendly name attribute if provided by the strategy
    sname = "strategy"
    try:
        if hasattr(strategy, "name") and getattr(strategy, "name"):
            sname = getattr(strategy, "name")
        elif hasattr(strategy, "__name__") and getattr(strategy, "__name__"):
            sname = getattr(strategy, "__name__")
        elif hasattr(strategy, "__class__") and hasattr(strategy.__class__, "__name__"):
            sname = strategy.__class__.__name__
    except Exception:
        sname = "strategy"

    # Write a per-run CSV into the run_dir created earlier
    csv_path = os.path.join(run_dir, f"{sname}_results.csv")

    seated_times = [t for t in m.seat_time.values() if t is not None]
    avg_time_to_seat = (
        (sum(seated_times) / len(seated_times)) if seated_times else float("nan")
    )
    max_cong = max(m.congestion_ts) if m.congestion_ts else 0
    avg_cong = (sum(m.congestion_ts) / len(m.congestion_ts)) if m.congestion_ts else 0.0

    header = [
        "timestamp",
        "seed",
        "num_passengers",
        "total_boarding_ticks",
        "seated_count",
        "avg_time_to_seat_ticks",
        "max_congestion",
        "avg_congestion",
    ]
    row = [
        int(time.time()),
        cfg.seed if cfg.seed is not None else "",
        cfg.num_passengers,
        m.total_ticks,
        m.seated_count,
        float(avg_time_to_seat),
        int(max_cong),
        float(avg_cong),
    ]

    write_header = not os.path.exists(csv_path)
    try:
        with open(csv_path, "a", encoding="utf-8") as cf:
            if write_header:
                cf.write(",".join(header) + "\n")
            cf.write(",".join(map(str, row)) + "\n")
    except Exception:
        print(f"Warning: failed to write metrics CSV to {csv_path}")

    # Optionally create a GIF from the frames we saved
    if auto_make_gif and save_frames:
        # GIF will be created inside the per-run directory next to the frames folder
        gif_out = os.path.join(run_dir, f"{sname}_animation.gif")

        # Try to call the imported make_gif() if available; otherwise import dynamically
        try:
            if make_gif is None:
                # dynamic import
                import importlib

                mod = importlib.import_module("make_gif_from_text_frames")
                func = getattr(mod, "make_gif")
            else:
                func = make_gif
            # Call make_gif, include font_path only if provided to satisfy type hints
            if gif_font:
                func(
                    frames_dir,
                    gif_out,
                    duration_ms=gif_duration,
                    font_path=gif_font,
                    font_size=gif_font_size,
                    scale=gif_scale,
                )
            else:
                func(
                    frames_dir,
                    gif_out,
                    duration_ms=gif_duration,
                    font_size=gif_font_size,
                    scale=gif_scale,
                )
        except Exception as e:
            print(f"Warning: failed to auto-create GIF: {e}")

    return m, plane, passengers


# 7) METRIC SUMMARIZATION


def summarize(m: Metrics) -> Dict[str, float]:
    seated_times = [t for t in m.seat_time.values() if t is not None]
    avg_time_to_seat = (
        (sum(seated_times) / len(seated_times)) if seated_times else float("nan")
    )
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
    # Choose a boarding strategy to run in the example. Use the module-level
    # default (back_to_front) but allow it to be changed here easily.
    strategy = back_to_front

    metrics, plane, passengers = run_once(cfg, boarding_strategy=strategy)

    stats = summarize(metrics)
    sname = getattr(
        strategy, "name", getattr(strategy, "__name__", strategy.__class__.__name__)
    )
    print(f"\nBoarding Simulation — Single Run Summary (strategy={sname})")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Optional quick visualization in console
    # plane.show_plane(mode="status")  # uncomment to see final layout
