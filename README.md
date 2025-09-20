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

**Potential Clients:** Southwest Airlines, Spirit Airlines (TBD)

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

This project demonstrates the use of **discrete-event simulation** and **Monte Carlo experimentation**—core tools in **Industrial Engineering & Operations Research (IEOR)**.

---

## Methodology

### Simulation Model

Implemented in an **object-oriented programming framework** with three main modules:

* **Plane Module** – Generates seating arrangement & overhead bin matrix.
* **Passenger Module** – Models passengers as agents with stochastic attributes:

  * Arrival time (Poisson arrivals)
  * Walking speed
  * Luggage & stowage behavior
  * Boarding group assignment
* **Simulation Engine** – Executes arrivals, aisle congestion, and seating under different heuristics, with random fluctuations such as swapped positions or delayed stowage.

### Analytic Techniques

* Performance evaluation of existing strategies.
* Sensitivity analysis of passenger attributes & random fluctuations.
* Monte Carlo simulations (10, 30, 100+ runs) for statistical reliability.
* Potential optimization of **hybrid strategies**.

---

## Desired Scope of Results

The study will compare and report on:

* **Total boarding time**
* **Average & variance of individual boarding times**
* **Amount & distribution of congestion time**
* **Variance of congestion across strategies**

**Deliverables:**

* Simulation code
* Statistical analyses
* Visualizations of results
* Recommendations for effective boarding strategies

---

## Repository Structure (planned)

```
plane-boarding-sim/
│── src/                 # Simulation code
│── data/                # Passenger distributions, input parameters
│── notebooks/           # Analysis & experiments
│── reports/             # Proposal, progress, draft, final reports
│── README.md            # Project overview
│── LICENSE              # BSD 2-Clause License
```

---

## License

This project is for **educational purposes only**.
Licensed under the [BSD 2-Clause License](./LICENSE).