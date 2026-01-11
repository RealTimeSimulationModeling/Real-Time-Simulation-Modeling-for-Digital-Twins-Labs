# Lab 1: Building Your First Simulation in Python

**A foundational lab on discrete-event simulation using only basic Python**

---

## Overview

This lab teaches you to build a discrete-event simulation from scratch—without any simulation frameworks. You'll model a single-server queue (a coffee shop with one barista) using only Python's standard library.

### Why This Lab?

Before learning simulation frameworks like SimPy, you need to understand what happens "under the hood":
- How loops drive simulations forward in time
- How state variables track system condition
- How random numbers create stochastic behavior
- How performance metrics are calculated

By building it manually first, you'll deeply understand discrete-event simulation concepts.

---

## Learning Objectives

- ✅ Understand discrete-event simulation mechanics
- ✅ Generate random arrivals using exponential distribution
- ✅ Generate random service times using uniform distribution
- ✅ Implement queue logic (when do customers wait?)
- ✅ Calculate key performance indicators (wait time, utilization, etc.)
- ✅ Analyze the relationship between server utilization and wait times
- ✅ Appreciate stochastic variability in simulation results

---

## The Scenario

You're analyzing a **coffee shop with one barista** (single-server queue):

- **Customers arrive randomly** (exponential inter-arrival times, mean = 3 minutes)
- **Service times are random** (uniform distribution, 2-5 minutes)
- **One barista serves one customer at a time** (FIFO discipline)
- **Customers wait in line** if the barista is busy

**Your goal**: Calculate wait times, server utilization, and explore system behavior.

---

## Files in This Lab

| File | Purpose |
|------|---------|
| `LAB_GUIDE.md` | Comprehensive lab instructions with theory and experiments |
| `coffee_shop_sim.py` | Complete solution with detailed comments |
| `coffee_shop_sim_starter.py` | Starter template with TODOs for students |
| `QUICKSTART.md` | Get running in 10 minutes |
| `README.md` | This file - overview and quick reference |

---

## Quick Start (10 Minutes)

### Option 1: Run the Complete Solution

```bash
# Navigate to lab directory
cd Lab1-First-Python-Simulation

# Run the simulation
python coffee_shop_sim.py
```

**You'll see**:
```
--- Simulating 100 Customers ---

==================================================
           SIMULATION RESULTS
==================================================

Input Parameters:
  Mean Interarrival Time: 3.00 minutes
  Service Time Range:     2.00 - 5.00 minutes
  Number of Customers:    100

Performance Metrics:
  Average Wait Time:      2.34 minutes
  Maximum Wait Time:      12.45 minutes
  Probability of Waiting: 72.00%
  Server Utilization:     87.23%
  Average Time in System: 5.89 minutes
  Average Service Time:   3.55 minutes
...
```

### Option 2: Complete the Starter Template

```bash
# Open the starter file
code coffee_shop_sim_starter.py

# Complete the TODOs (there are 15 of them)

# Run your code
python coffee_shop_sim_starter.py
```

---

## Installation Requirements

**Python Version**: 3.7 or higher

**Required Libraries**: None! (Uses only Python standard library)
- `random` - for generating random numbers
- `math` - for logarithm (exponential distribution)

No `pip install` needed!

---

## Key Concepts You'll Learn

### 1. Discrete-Event Simulation

The simulation advances customer-by-customer (event-by-event), not second-by-second:

```python
for customer_num in range(1, NUM_CUSTOMERS + 1):
    # Process this customer's complete journey
    arrival_time = ...
    service_time = ...
    wait_time = ...
```

### 2. Exponential Distribution for Arrivals

Random arrivals are modeled with exponential inter-arrival times:

```python
interarrival_time = -math.log(random.random()) * MEAN_INTERARRIVAL_TIME
```

**Why?** This creates a Poisson process (memoryless random arrivals).

### 3. The Queue Logic

The magic line that creates the queue:

```python
time_service_begins = max(arrival_time, time_server_is_free)
```

**If** customer arrives while server is free → immediate service (no wait)
**Else** customer arrives while server is busy → must wait (queue forms!)

### 4. Server Utilization

The fraction of time the server is busy:

```python
server_utilization = (total_busy_time) / (total_simulation_time)
```

**Key insight**: As utilization → 100%, wait times → ∞ (exponentially!)

---

## Experiments to Run

### Experiment 1: Stochastic Variability

Run 10 times without changing anything. Observe how results vary.

**Insight**: Simulation results have randomness. Need multiple replications for reliability.

### Experiment 2: Increase Arrival Rate

Change `MEAN_INTERARRIVAL_TIME = 2.0` (customers arrive faster)

**Expected**: Wait times ↑, Server utilization ↑

### Experiment 3: Slower Service

Change `MAX_SERVICE_TIME = 8.0` (service takes longer)

**Expected**: Wait times ↑, Server utilization ↑

### Experiment 4: The Utilization Curve

Run with different interarrival times to achieve 50%, 70%, 90%, 100% utilization.

**Plot**: Utilization (x-axis) vs. Average Wait Time (y-axis)

**Expected**: Exponential growth as utilization → 100%

---

## Expected Results

With default parameters:
- **Mean Interarrival Time**: 3.0 minutes
- **Service Time**: Uniform(2, 5) → average 3.5 minutes
- **Expected Utilization**: 3.5 / 3.0 ≈ 117% (unstable!)

**Typical output**:
- Average Wait Time: 5-15 minutes (varies due to randomness)
- Probability of Waiting: 60-80%
- Server Utilization: 85-95%

**Note**: System is near the stability boundary, so results are highly variable!

For stable results, try `MEAN_INTERARRIVAL_TIME = 5.0`:
- Expected Utilization: 3.5 / 5.0 = 70%
- Average Wait Time: ~2 minutes
- More consistent results across runs

---

## Key Performance Indicators (KPIs)

| KPI | Formula | Meaning |
|-----|---------|---------|
| **Average Wait Time** | `sum(waits) / num_customers` | How long customers wait on average |
| **Max Wait Time** | `max(waits)` | Worst-case customer experience |
| **Probability of Waiting** | `(customers_who_waited) / total` | Likelihood of encountering a queue |
| **Server Utilization** | `busy_time / total_time` | Fraction of time server is working |
| **Avg Time in System** | `wait_time + service_time` | Total time customer spends in shop |

---

## Analysis Questions

Answer these after completing the experiments:

1. **Variability**: How much do results vary between runs? What does this tell you about relying on a single simulation?

2. **Utilization Threshold**: At what utilization level do wait times become "unacceptable" (e.g., > 5 minutes)?

3. **Business Trade-off**: You're the shop owner. Higher utilization = efficient use of labor. But high utilization = long waits = unhappy customers. What utilization would you target?

4. **Ways to Reduce Wait Time**:
   - Hire a second barista?
   - Speed up service (better training, faster espresso machine)?
   - Reduce demand (raise prices to decrease arrivals)?
   - Which is most cost-effective?

5. **Realism**: This model makes simplifying assumptions. How might a real coffee shop differ?
   - Some customers abandon the queue if it's too long
   - Service time might depend on drink complexity (simple coffee vs. elaborate latte)
   - Multiple servers with different skill levels
   - Peak hours (time-varying arrival rates)

---

## Troubleshooting

### Problem: "Math domain error"

**Cause**: `math.log()` received 0 (very rare)

**Fix**: Ensure you're using `random.random()` not `random.randint()`

### Problem: Negative wait times

**Cause**: Used `min()` instead of `max()` for service start time

**Fix**: `time_service_begins = max(arrival_time, time_server_is_free)`

### Problem: Utilization > 100%

**Cause**: Arrivals faster than service (unstable system!)

**Fix**: This is correct! System is unstable. The queue grows without bound. Increase interarrival time to stabilize.

### Problem: Results don't match analytical formulas

**Cause**: Simulation is stochastic; results vary

**Fix**: Run more customers (500-1000) or multiple replications to stabilize results

---

## Extension Ideas

Once you've completed the basic lab:

1. **Add Visualization**: Plot histogram of wait times using `matplotlib`

2. **Multiple Replications**: Run 20 simulations, calculate mean ± std deviation

3. **Warm-Up Period**: Discard first 100 customers to avoid initialization bias

4. **Two Servers**: Model a shop with 2 baristas (much more complex!)

5. **Time-Varying Arrivals**: Model morning rush vs. slow afternoon

6. **Customer Abandonment**: Customers leave if wait > 10 minutes (balking)

---

## What's Next?

### Lab 2: Coffee Shop with SimPy

In the next lab, you'll rebuild this same system using **SimPy**, a discrete-event simulation framework.

You'll see how SimPy simplifies:
- Event scheduling (no manual loop!)
- Resource management (automatic queue handling)
- Process-based modeling (customer "processes")
- Statistical collection

**By doing Lab 1 first**, you'll appreciate what SimPy does for you and understand the underlying mechanics.

---

## Additional Resources

### Theory

- **Queuing Theory**: M/M/1 queue (analytical formulas for comparison)
- **Stochastic Processes**: Poisson arrivals, exponential service
- **Little's Law**: `L = λ × W` (relates queue length, arrival rate, wait time)

### Python

- Python `random` module: https://docs.python.org/3/library/random.html
- Python `math` module: https://docs.python.org/3/library/math.html

### Books

- Law, A.M. (2015). *Simulation Modeling and Analysis* (5th ed.)
- Banks, J. (2010). *Discrete-Event System Simulation* (5th ed.)

---

## Deliverables

Submit:

1. **Your completed Python script** (from starter template or your own)
2. **Experiment results document** (answers to all 5 experiments)
3. **Analysis summary** (1-2 pages answering the business questions)

**Format**: Code (.py file) + Document (.pdf or .md)

**Due**: [Set by instructor]

---

## Tips for Success

1. **Read the theory first**: Understand exponential distribution and queue logic before coding

2. **Trace through manually**: Follow Customer #1 and #2 on paper to understand the loop logic

3. **Start with the starter template**: The TODOs guide you step-by-step

4. **Print intermediate values**: Add `print()` statements inside the loop to debug

5. **Run small first**: Start with `NUM_CUSTOMERS = 10` to see detailed output

6. **Experiment systematically**: Change one parameter at a time

7. **Document observations**: Write down what you observe as you experiment

---

## Common Student Questions

**Q: Why use exponential distribution for arrivals?**
A: It models truly random, memoryless arrivals (like real customers). Each arrival is independent of the last.

**Q: What does "memoryless" mean?**
A: The time until the next arrival doesn't depend on how long since the last arrival. If you've been waiting 5 minutes, you're no more likely to see a customer in the next minute than if you'd been waiting 1 minute.

**Q: Why is utilization > 100% possible?**
A: It means arrivals are faster than service on average. The queue grows forever (unstable system). In reality, the shop would run out of space or customers would abandon the queue.

**Q: My results don't match the analytical M/M/1 formulas. Why?**
A: (1) This is M/U/1 (uniform service, not exponential), (2) Simulation is stochastic (varies), (3) Finite run length introduces bias. With 1000+ customers, results should converge closer to theory.

**Q: How many customers should I simulate?**
A: For stable results, use 500-1000. For fast experiments, 100 is okay. For publication-quality, 10,000+ with multiple replications.

**Q: Can I use NumPy instead of math?**
A: Yes! `np.random.exponential(MEAN_INTERARRIVAL_TIME)` is even better. But we're using only standard library to keep it simple.

---

## Acknowledgments

This lab is inspired by:
- Chapter 1 of Law (2015) *Simulation Modeling and Analysis*
- Classic queuing theory pedagogy
- Countless students who've learned simulation by building it from scratch

---

**You're now ready to build your first simulation!**

Start with `QUICKSTART.md` for the fastest path, or dive into `LAB_GUIDE.md` for comprehensive understanding.

**Have fun exploring the fascinating world of discrete-event simulation!**
