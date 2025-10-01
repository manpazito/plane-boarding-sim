# Plane Boarding Simulator

**Evaluating Boarding Strategies Through Stochastic Simulation**

This is a group project for **INDENG 174: Simulation for Enterprise-Scale Systems** at UC Berkeley (Fall 2025).
Our goal is to create a **plane boarding simulator** that models passenger arrivals and evaluates different airline boarding heuristics using discrete-event simulation.

---

## Team

* **Mathew Mouchamel** — [mathewmouchamel@berkeley.edu](mailto:mathewmouchamel@berkeley.edu)
* **Ali Younis** — [ayn1s@berkeley.edu](mailto:ayn1s@berkeley.edu)
* **Harry Ilanyan** — [harry\_ila@berkeley.edu](mailto:harry_ila@berkeley.edu)
* **Manuel A. Martinez Garcia** — [manpazito@berkeley.edu](mailto:manpazito@berkeley.edu)

---

## Significance

Boarding efficiency directly impacts:

* **Airline profitability** (reduced turnaround times).
* **On-time departures** (DOT punctuality standards).
* **Customer satisfaction** (reduced congestion and unpredictability).

Current methods are often inefficient, leading to:

* Aisle congestion.
* Uneven overhead bin usage.
* Unpredictable boarding times.

By developing a robust simulation framework, this project addresses a **real-world enterprise-scale systems engineering problem**. The results will quantify trade-offs between **speed, congestion, and passenger experience**, potentially informing both **academic research** and **airline industry policy decisions**.

---

## Methodology

### Simulation Model

Implemented in an **object-oriented programming framework** with three main modules:

* **Plane Module** – Generates seating arrangement & overhead bin matrix.
* **Passenger Module** – Models passengers as agents with stochastic attributes:

  * Arrival time (Poisson arrivals)
  * Walking speed
  * Luggage & stowage behav
  * Boarding group assignment
* **Simulation Engine** – Executes arrivals, aisle congestion, and seating under different heuristics, with random fluctuations such as swapped positions or delayed stowage.

### Analytic Techniques

- Performance evaluation of existing strategies (random, back-to-front, WILMA, etc.)  
- Sensitivity analysis on passenger attributes (walking speeds, luggage mix, arrival patterns)  
- Monte Carlo replications (10–100 runs) for statistical reliability  
- Potential exploration of hybrid or adaptive strategies  

---

## Desired Scope of Results

The simulation will produce comparative results across boarding strategies, including:  

- **Total boarding time**  
- **Variance and distribution of individual boarding times**  
- **Congestion levels** (amount and location of aisle blocking)  
- **Robustness of strategies** under different passenger mixes  

**Deliverables include:**  
- Simulation code (object-oriented Python)  
- Statistical analyses of strategies  
- Visualizations (boarding time plots, congestion heatmaps)  
- Practical recommendations for effective boarding strategies  

---

## Repository Structure

```
plane-boarding-sim/
│── boarding_sim/         # Simulation code (plane, passenger, engine, data)
│   │── plane.py
│   │── passenger.py
│   │── simulation_engine.py
│   │── data.py
│── analysis/             # Jupyter notebooks, experiments, results
│── reports/              # Proposal, progress, draft, final reports
│── README.md             # Project overview
│── LICENSE               # BSD 2-Clause License
```
---

## Future Improvements  

The framework is designed to extend beyond this project:  

- Multi-door boarding (front + rear)
- First-class priority boarding  
- Wide-body and multi-cabin aircraft with priority rules  
- Dynamic or adaptive boarding policies  
- Applications to public transit systems (e.g., BART, buses)  
- More realistic behaviors 

---

## License

This project is for **educational purposes only**.
Licensed under the [BSD 2-Clause License](./LICENSE).