# Plane Boarding Simulator

**Evaluating Boarding Strategies Through Stochastic Simulation**

This is a group project for **INDENG 174: Simulation for Enterprise-Scale Systems** at UC Berkeley (Fall 2025).  
Our goal is to create a **plane boarding simulator** that models passenger arrivals and evaluates different airline boarding heuristics using discrete-event simulation.

---

## Initial Setup

Clone the repository and set up your environment.

```bash
git clone https://github.com/manpazito/plane-boarding-sim.git
cd plane-boarding-sim

python3 -m venv venv
source venv/bin/activate  # Windows PowerShell: .\venv\Scripts\Activate.ps1

pip install -r requirements.txt --quiet
```

If you skip the virtual environment, just make sure to still install the requirments:

```bash
python3 -m pip install -r requirements.txt --quiet
```

---

## Team

- **Mathew Mouchamel** — [mathewmouchamel@berkeley.edu](mailto:mathewmouchamel@berkeley.edu)
- **Ali Younis** — [ayn1s@berkeley.edu](mailto:ayn1s@berkeley.edu)
- **Harry Ilanyan** — [harry_ila@berkeley.edu](mailto:harry_ila@berkeley.edu)
- **Manuel A. Martinez Garcia** — [manpazito@berkeley.edu](mailto:manpazito@berkeley.edu)

---

## Significance

Boarding efficiency directly impacts:

- Airline profitability (reduced turnaround times)
- On-time departures (DOT punctuality standards)
- Customer satisfaction (reduced congestion and unpredictability)

Current methods are often inefficient, leading to:

- Aisle congestion
- Uneven overhead-bin usage
- Unpredictable boarding times

This simulation framework quantifies trade-offs between **speed, congestion, and passenger experience**, informing both **academic research** and **airline operations**.

### Research Inspiration

The project’s design was partially inspired by research on dynamic matching and pricing policies in shared mobility systems.  
One of the team members had previously explored similar optimization “games” while working under Professor Chiwei Yan at UC Berkeley, focusing on fictitious rideshare platforms that modeled how user behavior interacts with system-level matching and pricing strategies.  
That experience motivated the idea of framing airplane boarding as a **policy-driven simulation environment**, where different boarding heuristics can be tested and compared under controlled conditions.

---

## Overview

A discrete-time boarding simulator implemented in Python for analyzing different boarding strategies.
It supports stochastic passenger attributes, configurable strategies, and animated ASCII visualizations with GIF export.

---

## Features

- Single-aisle aircraft model with an L-shaped entrance + aisle
- Agent-based passengers with random walking and stowing behaviors
- Pluggable boarding strategies (`back_to_front`, `front_to_back`, `random_order`, `wilma`, `grouped_*`)
- Deterministic `perfect_queue` for reproducibility
- Console animation, saved frames, and optional GIF generation (via Pillow)
- Per-run results organized in `results/{strategy}_{timestamp}/`

---

## Repository Layout

```
plane-boarding-sim/
├── LICENSE
├── README.md
├── analysis.ipynb
├── src/
│   ├── plane.py
│   ├── passenger.py
│   ├── basic_strategies.py
│   ├── simulation.py
│   └── make_gif_from_text_frames.py
├── results/              # runtime outputs
└── visuals/              # figures for reports
```

---

## Dependencies

- Python 3.10+ (tested with 3.13)
- Pillow (for GIF creation)
- NumPy (used by utility code; not required for the core loop)

You can install them manually or use the provided setup scripts.

---

## Quick Start

From the repository root:

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

This run:

- Executes one simulation with `back_to_front`
- Saves ASCII frames under `results/`
- Generates an animated GIF if Pillow is installed

---

## Output Structure

Each run with `save_frames=True` creates:

```
results/{strategy}_{timestamp}/
├── {strategy}_animation_frames/
├── {strategy}_animation.gif
└── {strategy}_results.csv
```

The `results/` folder is ignored by Git. Commit only selected artifacts if needed.

---

## Main API

- `SimConfig` — simulation parameters (`num_rows`, `num_passengers`, `p_have_bag`, etc.)
- `run_once()` — runs one experiment and returns `(metrics, plane, passengers)`

Key flags:

- `save_frames` — save ASCII frames
- `auto_make_gif` — generate GIF automatically
- `perfect_queue` — deterministic ordering for reproducible visuals

---

## Boarding Strategies

Defined in `src/basic_strategies.py` as callable objects:

- `back_to_front`
- `front_to_back`
- `random_order`
- `wilma`
- `grouped_*` (e.g. `grouped_5_6`)

Use them via `run_once(cfg, boarding_strategy=...)`.

---

## Visualization

Frames render the plane as ASCII with an “ENT” entrance column and aisle.
Saved frames can be converted to GIFs using `src/make_gif_from_text_frames.py`.

---

## Reproducibility

- Control randomness via `cfg.seed`
- Set `perfect_queue=True` for deterministic visuals
- Aggregate CSV outputs across runs for batch experiments

---

## Development Notes

- Look into cleaner visual creation
- Research passenger instances & add more features for real-world accuracy
- Create skeleton code structure to make project open for attempts at more optimal boarding policies
- Make `plane.py` more robust (multiple doors multiple aisles, etc.)

---

## License

This project is licensed under the [BSD 2-Clause License](https://github.com/manpazito/plane-boarding-sim/blob/main/LICENSE).
