import os
import sys
import numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

# Resolve repo root from this file's location
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"

for p in (SRC_PATH, REPO_ROOT):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

from simulation import SimConfig, run_once  # type: ignore
from custom_strategy import STRATEGIES


def load_strategy_passengers(prefix, base="../results"):
    """
    Finds the folder starting with `prefix` inside `base`,
    loads all CSV files inside it, and returns a list of DataFrames.
    """
    # Find the results directory that matches prefix
    folder = next(f for f in os.listdir(base) if f.startswith(prefix))
    folder_path = os.path.join(base, folder)

    # Load all CSVs inside that folder
    dfs = [
        pd.read_csv(os.path.join(folder_path, fname))
        for fname in os.listdir(folder_path)
        if fname.endswith(".csv")
    ]
    return dfs


def run_simulations_N(
    strategy_name: str,
    strategy_func,
    N: int = 10,
):
    """
    Run a given strategy N times, collect per-passenger data from each run
    directly from run_once(), and return ONE combined DataFrame with all runs.

    Each row has:
      - passenger info (target_row, letter, etc.)
      - entry/seat/time_to_seat
      - run index (0..N-1)
      - strategy name
    """

    all_rows = []

    for run_idx in range(N):
        cfg = SimConfig(seed=np.random.randint(0, 1_000_000))  # new randomness per run
        metrics, plane, passengers = run_once(
            cfg=cfg,
            boarding_strategy=strategy_func,
            save_frames=False,
            perfect_queue=True,
        )

        # Recreate the same per-passenger data that simulation.py writes to CSV
        for p in passengers:
            entry = metrics.entry_time.get(p.pid)
            seat = metrics.seat_time.get(p.pid)

            if entry is None or seat is None:
                time_to_seat = None
            else:
                try:
                    time_to_seat = int(seat) - int(entry)
                except Exception:
                    time_to_seat = None

            row = {
                "pid": p.pid,
                "target_row": p.target_row,
                "target_letter": p.target_letter,
                "missed": bool(getattr(p, "missed", False)),
                "entry_time": entry,
                "seat_time": seat,
                "time_to_seat": time_to_seat,
                "has_bag": bool(getattr(p, "has_bag", False)),
                "walk_ticks": getattr(p, "walk_ticks", None),
                "stow_ticks": getattr(p, "stow_ticks", None),
                "lane": getattr(p, "lane", None),
                "entry_door": getattr(p, "entry_door", None),
                "run": run_idx,
                "strategy": strategy_name,
            }
            all_rows.append(row)

    final_df = pd.DataFrame(all_rows)
    return final_df


def save_strategy_results(
    strategy_name: str,
    df: pd.DataFrame,
    runs: int = 10,
    out_dir: str = "../results",
):
    """
    Save the combined passenger-level results for a strategy into ../results.

    The filename includes the number of runs, e.g.:
      back_to_front_passengers_10runs_combined.csv
    """

    os.makedirs(out_dir, exist_ok=True)

    filename = f"{strategy_name}_passengers_{runs}runs_combined.csv"
    save_path = os.path.join(out_dir, filename)

    df.to_csv(save_path, index=False)
    print(f"Saved combined passenger results → {save_path}")
