# Plane Boarding Simulator

A discrete-time, agent-based simulation framework for studying commercial aircraft boarding procedures.
This project models passengers, aircraft geometry, overhead bins, and movement constraints to support controlled experiments in boarding efficiency.

Developed for **INDENG 174: Simulation for Enterprise-Scale Systems**, University of California, Berkeley (Fall 2025).

---

## Overview

The simulator represents an aircraft cabin using seats, overhead bins, and one or more parallel aisle lanes. Passengers are modeled as agents with heterogeneous walking cadences, stow times, baggage characteristics, and seat assignments. During each simulation tick, passengers:

- enter through front and/or rear doors
- traverse available aisle lanes
- stow baggage in overhead bins
- wait when blocked
- take their seat when their row is accessible

The simulation records seat times, entry times, congestion per tick, and total boarding duration. Optional ASCII and GIF-based visualizations support qualitative inspection.

The framework is designed for experimentation with queue-ordering strategies and sensitivity analyses.

---

# Installation (Recommended)

The repository includes **platform-specific setup scripts** that automatically:

- detect or validate the local Python installation
- create a `venv/` virtual environment
- install dependencies from `requirements.txt`
- set up `PYTHONPATH`
- provide a ready-to-run example that executes a small simulation

These scripts are the **primary and recommended way** to prepare the environment.

---

## Windows (PowerShell)

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

This script:

- locates a valid Python interpreter
- creates and activates `.\venv\`
- installs dependencies
- provides a quick test snippet:

```powershell
  setx PYTHONPATH "$PWD\src" >$null
  python - <<'PY'
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

To activate the environment later:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## macOS / Linux

From the repository root:

```bash
./scripts/setup.sh
```

This performs the same steps as the Windows script:

- creates `venv/`
- installs dependencies
- configures `PYTHONPATH`
- provides a short runnable test simulation

To activate later:

```bash
source venv/bin/activate
```

---

# Alternative Installation (Manual)

If you prefer to configure the environment yourself:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run a simulation:

```bash
python src/simulation.py --strategy back_to_front
```

Generate animation frames and a GIF:

```bash
python src/simulation.py --strategy steffen --save-frames
```

Disable deterministic queue ordering:

```bash
python src/simulation.py --strategy random --no-perfect-queue
```

Optional: Convert saved text frames to a GIF (standalone tool):

```bash
python src/make_gif_from_text_frames.py --frames-dir results/animations --out results/animations/animation.gif
```

---

# Programmatic Usage

```python
from simulation import SimConfig, run_once
from basic_strategies import back_to_front

cfg = SimConfig(num_rows=25, num_passengers=150, seed=42)
metrics, plane, passengers = run_once(
    cfg,
    boarding_strategy=back_to_front,
    perfect_queue=True,          # deterministic ordering within groups
    save_frames=False,           # set True to write per-tick ASCII frames
    auto_make_gif=False,         # set True (with save_frames) to auto-create GIF
    gif_duration=150,            # ms per GIF frame
    gif_scale=2,                 # scale factor for GIF rendering
)

print("Total boarding ticks:", metrics.total_ticks)
```

---

# Configuration Reference

### SimConfig Parameters

| Parameter                       | Description                                  | Default            |
| ------------------------------- | -------------------------------------------- | ------------------ |
| `num_rows`                      | Number of aircraft rows                      | 30                 |
| `seat_arrangement`              | Row layout (e.g., `[A B C aisle D E F]`)     | defaultArrangement |
| `bin_capacity_per_row`          | Overhead bin units per row                   | 4                  |
| `num_passengers`                | Number of passengers (capped by total seats) | 180                |
| `seat_letters`                  | Override seat labels                         | None               |
| `p_have_bag`                    | Probability passenger has carry-on           | 0.8                |
| `p_missed`                      | No-show probability                          | 0.02               |
| `walk_mean`, `walk_sd`          | Walking cadence distribution                 | 1.0, 0.2           |
| `stow_mean`, `stow_sd`          | Stow time distribution                       | 2.0, 0.5           |
| `seed`                          | RNG seed                                     | 42                 |
| `max_ticks`                     | Tick cutoff                                  | 10,000             |
| `collect_time_series`           | Track per-tick congestion                    | True               |
| `disable_no_shows_when_filling` | Force full-plane experiments                 | True               |

---

### run_once Keyword Arguments

| Argument                    | Meaning                             |
| --------------------------- | ----------------------------------- |
| `boarding_strategy`         | Callable defining passenger order   |
| `animate`                   | Show live ASCII animation           |
| `frame_delay`               | Animation timing                    |
| `save_frames`               | Persist per-tick ASCII snapshots    |
| `frames_dir`                | Directory for saved frames          |
| `perfect_queue`             | Remove intra-group randomness       |
| `auto_make_gif`             | Automatically convert frames to GIF |
| `gif_duration`              | Milliseconds per GIF frame          |
| `gif_font`, `gif_font_size` | Font settings for GIF               |
| `gif_scale`                 | Scaling factor for GIF rendering    |

---

# CLI

```
python src/simulation.py [OPTIONS]

--strategy NAME
--animate
--save-frames
--no-perfect-queue
```

Built-in strategies:

- front_to_back
- back_to_front
- random
- wilma
- steffen

---

# Output Structure

Each simulation produces:

```
results/{strategy}_{timestamp}/
    ├── {strategy}_animation_frames/    (optional)
    ├── {strategy}_animation.gif        (optional)
    ├── {strategy}_results.csv          (run-level summary)
    └── {strategy}_passengers.csv       (per-passenger detail)
```

### `{strategy}_results.csv` includes:

- total boarding ticks
- seated passenger count
- average seat time
- average and maximum congestion

### `{strategy}_passengers.csv` includes:

- passenger ID
- seat assignment
- entry and seat timestamps
- time-to-seat
- walking cadence, stow time
- door and lane used

---

# Custom Boarding Strategies

To define a custom strategy:

1. Copy `src/custom_strategy.py` into a new file in `src/` (e.g., `src/my_strategy.py`).
2. Modify the `CustomBoardingStrategy` class (rename, implement `__call__`).
3. Ensure it registers itself into `STRATEGIES` (the template does this for you).
4. Make sure the module is imported so registration happens:
   - Option A: add near the top of `src/simulation.py`:
     ```python
     # import your strategy module so it registers into STRATEGIES
     import my_strategy  # noqa: F401
     ```
   - Option B: in a notebook/script, `import my_strategy` before calling `run_once`.

Example:

```python
class MyStrategy(BoardingStrategy):
    name = "my_strategy"

    def __call__(self, passengers):
        return sorted(passengers, key=lambda p: (p.target_row, p.target_letter))
```

Use it:

```bash
python src/simulation.py --strategy my_strategy
```

---

# Examples and Notebooks

Located in `notebooks/`:

- `demo.ipynb`: single-run demonstration, optional GIF, shows intermediate states
- `analysis.ipynb`: multi-run analysis, comparative metrics, sensitivity analysis

---

# Reproducibility

- Setting `seed` ensures identical stochastic sampling.
- `perfect_queue=True` removes intra-group randomness.
- Deterministic simulation engine ensures repeatability given fixed inputs.

---

# Contributors

- Mathew Mouchamel — [mathewmouchamel@berkeley.edu](mailto:mathewmouchamel@berkeley.edu)
- Ali Younis — [ayn1s@berkeley.edu](mailto:ayn1s@berkeley.edu)
- Harry Ilanyan — [harry_ila@berkeley.edu](mailto:harry_ila@berkeley.edu)
- Manuel A. Martinez Garcia — [manpazito@berkeley.edu](mailto:manpazito@berkeley.edu)

---

# License

Released under the **BSD 2-Clause License**.
