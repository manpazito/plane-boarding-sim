# Plane Boarding Simulator

**Evaluating Boarding Strategies Through Stochastic Simulation**

This is a group project for **INDENG 174: Simulation for Enterprise-Scale Systems** at UC Berkeley (Fall 2025).
Our goal is to create a **plane boarding simulator** that models passenger arrivals and evaluates different airline boarding heuristics using discrete-event simulation.

---

## Team

- **Mathew Mouchamel** — [mathewmouchamel@berkeley.edu](mailto:mathewmouchamel@berkeley.edu)
- **Ali Younis** — [ayn1s@berkeley.edu](mailto:ayn1s@berkeley.edu)
- **Harry Ilanyan** — [harry_ila@berkeley.edu](mailto:harry_ila@berkeley.edu)
- **Manuel A. Martinez Garcia** — [manpazito@berkeley.edu](mailto:manpazito@berkeley.edu)

---

## Significance

Boarding efficiency directly impacts:

- **Airline profitability** (reduced turnaround times).
- **On-time departures** (DOT punctuality standards).
- **Customer satisfaction** (reduced congestion and unpredictability).

Current methods are often inefficient, leading to:

- Aisle congestion.
- Uneven overhead bin usage.
- Unpredictable boarding times.

By developing a robust simulation framework, this project addresses a **real-world enterprise-scale systems engineering problem**. The results will quantify trade-offs between **speed, congestion, and passenger experience**, potentially informing both **academic research** and **airline industry policy decisions**.

---

## Plane Boarding Simulator

Evaluating boarding strategies through a small, discrete-time plane boarding simulator implemented in Python.

This repository contains a compact simulation framework for experimenting with boarding heuristics, passenger behavior models, and visualizations (ASCII frames + GIFs). The code was developed during an academic project and is intended for research, exploration, and teaching.

## What’s in this version

- Single-aisle aircraft model with a dedicated "entrance" aisle cell (the aisle is represented as an L-shaped entrance + aisle in the ASCII rendering).
- Agent-based passengers with stochastic attributes:
  - carry-on probability (affects stow time)
  - no-show / missed-boarding probability
  - per-passenger walking and stow time distributions
- Pluggable boarding strategies implemented as named strategy objects (examples: `back_to_front`, `front_to_back`, `random_order`, `wilma`, `grouped_*`).
- Deterministic `perfect_queue` option for reproducible visualizations (fixes intra-group ordering).
- Console animation and per-tick ASCII frame saving; offline conversion of saved frames to animated GIFs (Pillow-based utility).
- Per-run output organization: `results/{strategy}_{timestamp}/` containing the frames directory, an animated GIF, and a per-run metrics CSV.

## Current repository layout

```
plane-boarding-sim/
├── LICENSE
├── README.md
├── analysis.ipynb        # Notebook to do user-friendly analysis
├── src/
│   ├── plane.py          # Plane geometry, seat map, ASCII rendering
│   ├── passenger.py      # Passenger agent, generator helper
│   ├── basic_strategies.py     # Named strategy objects (class-based)
│   ├── simulation.py     # run_once() engine, metrics, frame/GIF orchestration
│   └── make_gif_from_text_frames.py  # converts saved ASCII frames -> GIF
├── results/              # runtime outputs (animations, per-run folders) — ignored in git
└── visuals/              # miscellaneous images/figures used in reports
```

Notes:

- `src/` contains the runnable simulation code. Import `run_once` from `src/simulation.py` from notebooks or scripts.
- `results/` is used to store generated frames, GIFs and CSV metrics. This directory is ignored by Git in the project `.gitignore` so local experiments don't pollute the repo.

## Dependencies

- Python 3.10+ (tested with 3.13 in development environment)
- Pillow (for GIF creation)
- numpy (used by some utility code; not required for the core loop)

You can install the basics with:

```bash
python -m pip install -r requirements.txt --quiet
```

## Quick start (programmatic)

From the repository root you can run quick experiments by importing the engine. Use `PYTHONPATH=src` so the `src` package is on the import path:

```bash
PYTHONPATH=src python3 - <<'PY'
from simulation import SimConfig, run_once
from basic_strategies import back_to_front

cfg = SimConfig(num_rows=6, num_passengers=30, seed=42)
metrics, plane, passengers = run_once(
    cfg,
    boarding_strategy=back_to_front,
    save_frames=True,
    auto_make_gif=True,
    gif_duration=120,
    gif_scale=2,
)
print('Total ticks:', metrics.total_ticks)
PY
```

What this does:

- Runs a single simulation with `back_to_front` ordering.
- Saves per-tick ASCII snapshots into a per-run folder under `results/`.
- Automatically creates an animated GIF of the run (if `auto_make_gif=True` and Pillow is available).

## Output / results layout

When a run is executed with `save_frames=True`, the code creates a per-run directory under `results/`:

- `results/{strategy}_{timestamp}/`
  - `{strategy}_animation_frames/` — text frames named `{strategy}_frame_00000.txt`, `{strategy}_frame_00001.txt`, ...
  - `{strategy}_animation.gif` — optional animated GIF produced by the GIF utility
  - `{strategy}_results.csv` — CSV with one row describing the run metrics (ticks, congestion, etc.)

This layout keeps each experiment encapsulated and reproducible. Note that `results/` is gitignored by design — if you want to include a run artifact, add it to a different folder or commit the specific file(s) manually.

## Main API (short)

- `SimConfig` — dataclass containing simulation parameters (num_rows, num_passengers, p_have_bag, p_missed, seed, etc.).
- `run_once(cfg, boarding_strategy=..., save_frames=False, auto_make_gif=False, perfect_queue=True, ...)` — run a single experiment. Returns `(metrics, plane, passengers)`.

Important flags:

- `save_frames` — write ASCII frames to disk for later analysis / GIF creation.
- `auto_make_gif` — try to convert saved frames to GIF (requires Pillow).
- `perfect_queue` — when True the ordering inside boarding groups is made deterministic for reproducible visuals.

## Boarding strategies

Strategies are implemented in `src/basic_strategies.py` as class-like or callable objects with a `name` attribute. Examples exported by the module include:

- `back_to_front` — back-to-front ordering
- `front_to_back` — front-to-back ordering
- `random_order` — fully random boarding
- `wilma` — WILMA (window-middle-aisle) ordering
- `grouped_*` — grouped boarding factories (e.g., grouped_5-6)

Pass a strategy object to `run_once()` as ` boardi```````````````ng_strategy=<strategy> `.

## Visualization and ASCII frames

The plane rendering prints an L-shaped entrance (an "ENT" column) and an aisle. Aisle cells and entrance use a configurable symbol; when frames are saved they contain the human-readable ASCII that is later turned into a GIF by `src/make_gif_from_text_frames.py`.

If you want more control over GIF creation (font, scale, duration), pass `gif_*` params to `run_once()` or call `make_gif()` directly from `src/make_gif_from_text_frames.py`.

## Reproducibility and experiments

- Use `cfg.seed` to control randomness for repeatable experiments.
- Set `perfect_queue=True` to remove intra-group randomness so that saved frames are visually consistent between runs.
- The per-run CSV contains simple summary metrics; for larger experiment sweeps, use `run_once()` in loops and aggregate the CSVs centrally in `results/metrics/` or similar.

## Development notes / future work

- Add a small CLI wrapper (e.g., `scripts/run_sim.py`) to simplify running common experiments from the terminal.
- Add a `pyproject.toml` for reproducible environments.
- Add automated tests for core behaviors (aisle indexing, passenger generation, strategy ordering).
- Add optional post-run archive/cleanup of frames (e.g., delete frames after GIF created) as a configurable flag.

## License

BSD 2-Clause — see the `LICENSE` file.
