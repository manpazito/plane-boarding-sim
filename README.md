Here is an updated, clear, beginner-friendly README that **includes the Team section**, avoids emojis, and is written so **any reader** (classmates, instructors, recruiters, GitHub users) can understand the project easily.

You can paste this directly into your `README.md`.

---

# Plane Boarding Simulator

This project simulates how passengers board an airplane.
It allows different boarding methods (such as back-to-front, WILMA, Steffen, or custom methods) to be tested and compared based on boarding time, congestion, and overall efficiency.

The simulator models individual passengers, their walking speeds, bag-stowing times, seat assignments, and how they interact inside the airplane. Aircraft structures, doors, aisles, seats, and overhead bins are all modeled.

This project was developed for **INDENG 174: Simulation for Enterprise-Scale Systems**, UC Berkeley (Fall 2025).

---

## Team

- **Mathew Mouchamel** — [mathewmouchamel@berkeley.edu](mailto:mathewmouchamel@berkeley.edu)
- **Ali Younis** — [ayn1s@berkeley.edu](mailto:ayn1s@berkeley.edu)
- **Harry Ilanyan** — [harry_ila@berkeley.edu](mailto:harry_ila@berkeley.edu)
- **Manuel A. Martinez Garcia** — [manpazito@berkeley.edu](mailto:manpazito@berkeley.edu)

---

## Project Overview

This simulator uses a **discrete-time, agent-based model** to recreate the boarding process.
Each time step ("tick"), passengers:

- enter through a chosen door
- walk through the aisle
- stow their baggage
- wait if blocked
- sit in their assigned seats

The simulator tracks all interactions, timing, and congestion.
Results are written to a timestamped folder, and an optional ASCII animation or GIF can be generated.

The codebase is designed to be easy to extend, especially for writing your own boarding strategies.

---

## Key Features

### Aircraft Modeling

- Supports single-aisle or multi-aisle aircraft
- Supports front-door, rear-door, or dual-door boarding
- Seat arrangements and bin capacities are configurable
- ASCII visualization of the aircraft at each simulation tick

### Passenger Behavior

- Individualized walking speed
- Bag/no-bag behavior and stow times
- Entry door and lane assignment
- No-show probability
- Independent state tracking (walking, waiting, stowing, seated)

### Boarding Strategies

Built-in strategies include:

- Back-to-Front
- Front-to-Back
- Random
- WILMA (Window–Middle–Aisle)
- Steffen Method
- Grouped or Blocked boarding

Users can also create **custom strategies** through a simple plugin architecture.

### Simulation Engine

- Discrete-time update loop
- Congestion and timing metrics
- Reproducibility controls via random seeds
- Optional animation and GIF export

---

## Repository Structure

```
plane-boarding-sim/
│
├── README.md
├── LICENSE
├── requirements.txt
│
├── data/                      ← research papers and references
│
├── examples/                  ← Jupyter notebooks for analysis and demos
│   ├── analysis.ipynb
│   └── demo.ipynb
│
├── results/                   ← automatically-generated simulation outputs
│
├── scripts/
│   ├── setup.sh
│   └── setup.ps1
│
└── src/
    ├── simulation.py          ← main simulation loop
    ├── plane.py               ← airplane geometry + door/lane modeling
    ├── passenger.py           ← passenger movement and state logic
    ├── basic_strategies.py    ← built-in boarding strategies
    ├── custom_strategy.py     ← template for custom strategies
    └── make_gif_from_text_frames.py
```

---

## Installation

```bash
git clone https://github.com/manpazito/plane-boarding-sim.git
cd plane-boarding-sim

python3 -m venv venv
source venv/bin/activate                 # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Running a Simulation

Run with a built-in strategy:

```bash
python src/simulation.py --strategy back_to_front
```

Enable ASCII animation:

```bash
python src/simulation.py --strategy wilma --animate
```

Save animation frames and generate a GIF:

```bash
python src/simulation.py --strategy steffen --save-frames
```

Disable deterministic queueing:

```bash
python src/simulation.py --strategy random --no-perfect-queue
```

---

## Programmatic Usage

```python
from simulation import SimConfig, run_once
from basic_strategies import back_to_front

cfg = SimConfig(num_rows=25, num_passengers=150, seed=42)
metrics, plane, passengers = run_once(cfg, boarding_strategy=back_to_front)

print("Total boarding ticks:", metrics.total_ticks)
```

---

## Output Format

Each simulation run produces:

```
results/{strategy}_{timestamp}/
    ├── {strategy}_animation_frames/
    ├── {strategy}_animation.gif      (if --save-frames used)
    └── {strategy}_results.csv
```

The CSV file includes:

- Total boarding time
- Per-passenger entry time
- Per-passenger seat time
- Congestion by tick
- Average seating time
- Maximum congestion

---

## Creating Your Own Boarding Strategy

Copy the included template:

```bash
cp src/custom_strategy.py src/my_strategy.py
```

Edit the `__call__` method:

```python
class MyStrategy(BoardingStrategy):
    name = "my_strategy"

    def __call__(self, passengers):
        # Example: sort by row then seat letter
        return sorted(passengers, key=lambda p: (p.target_row, p.target_letter))
```

Run your strategy:

```bash
python src/simulation.py --strategy my_strategy
```

Your file automatically registers itself with the global strategy list.

---

## How the Simulation Works (High Level)

1. A plane is created with the specified number of rows, aisles, doors, and bins.
2. Passengers are generated with seat assignments, walking speeds, and bag properties.
3. A strategy determines the order passengers line up.
4. The simulation runs in small time steps:

   - passengers enter through assigned doors
   - move down aisles
   - stow bags
   - wait if blocked
   - sit when reaching their row

5. The simulator records all times and outputs results.

The system can be used to compare strategies under controlled conditions.

---

## Reproducibility

- Set `seed` in `SimConfig` to reproduce results exactly
- Use `--no-perfect-queue` for fully randomized passenger ordering
- CSV data can be aggregated in `examples/analysis.ipynb`

---

## License

This project is licensed under the BSD 2-Clause License.
