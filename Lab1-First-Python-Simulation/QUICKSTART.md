# Lab 1: Quick Start Guide

**Get your first simulation running in 10 minutes!**

---

## The 10-Minute Path

### Step 1: Run the Complete Solution (2 minutes)

```bash
# Navigate to lab directory
cd Lab1-First-Python-Simulation

# Run the simulation
python coffee_shop_sim.py
```

**You should see**:
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
  Average Wait Time:      3.45 minutes
  Maximum Wait Time:      15.23 minutes
  Probability of Waiting: 68.00%
  Server Utilization:     89.12%
  Average Time in System: 6.91 minutes
...
```

✅ **Success!** You've run your first simulation.

### Step 2: Understand What Just Happened (3 minutes)

**The Scenario**: One barista serving random customers

**Key Metrics**:
- **Average Wait Time (3.45 min)**: How long customers wait on average
- **Server Utilization (89%)**: Barista is busy 89% of the time
- **Probability of Waiting (68%)**: 68% of customers had to wait

**The Question**: Is this good or bad?

**The Answer**: Server is very busy (89% utilization), but customers wait ~3.5 minutes on average. Most businesses target 70-80% utilization for good service.

### Step 3: Experiment with Parameters (5 minutes)

Open `coffee_shop_sim.py` in your editor and find these lines at the top:

```python
MEAN_INTERARRIVAL_TIME = 3.0  # Average time between arrivals
MIN_SERVICE_TIME = 2.0        # Minimum service time
MAX_SERVICE_TIME = 5.0        # Maximum service time
NUM_CUSTOMERS_TO_SIMULATE = 100
```

**Experiment A: Hire faster barista**

Change:
```python
MAX_SERVICE_TIME = 4.0  # Was 5.0
```

Run again: `python coffee_shop_sim.py`

**Observe**: Wait times decrease! Utilization decreases!

**Experiment B: Morning rush**

Change:
```python
MEAN_INTERARRIVAL_TIME = 2.0  # Was 3.0 (customers arrive more frequently!)
MAX_SERVICE_TIME = 5.0  # Back to original
```

Run again: `python coffee_shop_sim.py`

**Observe**: Wait times EXPLODE! Utilization approaches 100%!

**Experiment C: Slow day**

Change:
```python
MEAN_INTERARRIVAL_TIME = 6.0  # Customers arrive less frequently
```

Run again: `python coffee_shop_sim.py`

**Observe**: Almost no waits! But utilization is low (barista is often idle).

✅ **You've discovered the utilization-wait time trade-off!**

---

## The 30-Minute Path (If You Want to Code)

### Step 1: Open the Starter Template

```bash
code coffee_shop_sim_starter.py
```

Or your favorite editor!

### Step 2: Complete the TODOs

You'll see 15 TODOs like:

```python
# TODO 1: Calculate Inter-Arrival Time using exponential distribution
# Formula: -math.log(random.random()) * MEAN_INTERARRIVAL_TIME
interarrival_time = # YOUR CODE HERE
```

**Hints**:
- TODO 1-3: Generate random times
- TODO 4-8: Calculate when customer gets served and how long they wait
- TODO 9-10: Store results and update state for next customer
- TODO 11-15: Calculate and print metrics

### Step 3: Run Your Code

```bash
python coffee_shop_sim_starter.py
```

**If you get errors**: Compare with `coffee_shop_sim.py` (the solution)

### Step 4: Test Your Understanding

Run your completed code with these parameters:

```python
MEAN_INTERARRIVAL_TIME = 5.0
MIN_SERVICE_TIME = 2.0
MAX_SERVICE_TIME = 5.0
NUM_CUSTOMERS = 100
```

**Expected results** (approximately, will vary due to randomness):
- Average Wait Time: ~1.5 minutes
- Server Utilization: ~70%
- Probability of Waiting: ~50%

**Does your code produce reasonable results?** ✅ Great! You've built your first simulation!

---

## Quick Concept Check

After running the simulation, can you answer these?

### Q1: What does "MEAN_INTERARRIVAL_TIME = 3.0" mean?

<details>
<summary>Click to reveal answer</summary>

On average, a new customer arrives every 3 minutes. The actual time between arrivals varies randomly (exponential distribution).
</details>

### Q2: Why does the Average Wait Time change when you run the same code twice?

<details>
<summary>Click to reveal answer</summary>

The simulation uses random numbers! Each run is different. This is called "stochastic variability." To get stable results, you'd need to run multiple replications or simulate more customers.
</details>

### Q3: If server utilization is 95%, what happens to wait times?

<details>
<summary>Click to reveal answer</summary>

They become VERY LONG! As utilization approaches 100%, wait times grow exponentially. Even a small increase in arrivals can cause huge waits.
</details>

### Q4: What's the difference between "Wait Time" and "Time in System"?

<details>
<summary>Click to reveal answer</summary>

- **Wait Time**: Time customer spends waiting in line
- **Time in System**: Wait Time + Service Time (total time from arrival to departure)
</details>

---

## The One Line That Makes It All Work

Find this line in the code:

```python
time_service_begins = max(arrival_time, time_server_is_free)
```

**This is the queue logic!**

**Scenario A**: Customer arrives at time 10. Server is free at time 8.
- `max(10, 8) = 10`
- Service begins immediately when customer arrives (no wait!)

**Scenario B**: Customer arrives at time 10. Server is free at time 15.
- `max(10, 15) = 15`
- Service begins when server becomes free (customer waits 5 minutes!)

**This one line implements the entire waiting queue.**

---

## Quick Experiments (5 minutes each)

### Experiment 1: Variability

Run the same code 5 times (don't change parameters).

**Record**: Average Wait Time from each run

**Question**: How much does it vary? ±10%? ±50%?

**Insight**: Simulation results aren't deterministic. Always run multiple replications!

### Experiment 2: The Breaking Point

Try these `MEAN_INTERARRIVAL_TIME` values:

| Value | Expected Utilization | What Happens? |
|-------|----------------------|---------------|
| 10.0  | ~35%                 | Almost no waits |
| 5.0   | ~70%                 | Moderate waits |
| 4.0   | ~87%                 | Getting long... |
| 3.5   | ~100%                | VERY long waits! |
| 3.0   | >100%                | System unstable! |

**Question**: At what utilization does service become "unacceptable"?

**Business Insight**: Most businesses target 70-80% utilization to balance efficiency and service quality.

### Experiment 3: Capacity Planning

**Scenario**: You're the coffee shop owner. Currently:
- Mean interarrival = 3.0 minutes
- Service time = 2-5 minutes (avg 3.5)
- Utilization ≈ 117% (UNSTABLE!)
- Wait times are unacceptable

**Options**:
A. Hire a second barista (halves the load)
B. Buy a faster espresso machine (`MAX_SERVICE_TIME = 4.0`)
C. Raise prices to reduce demand (`MEAN_INTERARRIVAL_TIME = 4.0`)

**Task**: Model each option. Which reduces wait times most?

**Hint**: Change one parameter at a time and compare Average Wait Time.

---

## Troubleshooting

### ❌ Error: "Math domain error"

**Problem**: `math.log()` received 0

**Fix**: Very rare! Just run again. (In production code, add: `random.random() + 1e-10`)

### ❌ My wait times are all zero!

**Problem**: You're not updating `time_server_is_free` at the end of the loop

**Fix**: Add this at the end of your loop:
```python
time_server_is_free = time_service_ends
```

### ❌ I'm getting negative wait times!

**Problem**: You used `min()` instead of `max()`

**Fix**: Change to:
```python
time_service_begins = max(arrival_time, time_server_is_free)
```

Service begins at the **LATER** time, not the earlier!

### ❌ Server utilization is > 100%!

**Not a bug!** This means the system is unstable:
- Customers arrive faster than they're served
- The queue grows forever
- In reality, customers would abandon the queue

**Fix**: Increase `MEAN_INTERARRIVAL_TIME` to make arrivals slower.

---

## What You've Learned (In 10 Minutes!)

✅ How discrete-event simulation works (loop through events)

✅ How random numbers create stochastic behavior (exponential, uniform distributions)

✅ How queues form (when arrivals > service capacity)

✅ How to calculate performance metrics (wait time, utilization, etc.)

✅ The relationship between utilization and wait times (exponential growth!)

✅ Why simulation results vary (randomness = variability)

**Pretty good for 10 minutes!**

---

## Next Steps

### Level 1: Completed Quickstart (You Are Here!)

You can run the simulation and experiment with parameters.

### Level 2: Complete the Lab Guide

Read `LAB_GUIDE.md` for:
- Detailed theory (why exponential distribution?)
- Step-by-step coding instructions
- 5 structured experiments
- Analysis questions
- Extension challenges

**Time**: 2-3 hours

### Level 3: Build From Scratch

Use `coffee_shop_sim_starter.py` and complete all TODOs without peeking at the solution.

**Time**: 1-2 hours

### Level 4: Extensions

Try the challenges:
- Visualize with `matplotlib`
- Add a second server
- Model time-varying arrivals (rush hours)
- Implement customer abandonment

**Time**: Variable (1-5 hours depending on challenge)

---

## One-Page Cheat Sheet

### Key Formulas

```python
# Exponential inter-arrival time (random arrivals)
interarrival_time = -math.log(random.random()) * mean_time

# Uniform service time (simple random service)
service_time = random.uniform(min_time, max_time)

# Queue logic (when does service begin?)
time_service_begins = max(arrival_time, time_server_is_free)

# Wait time
wait_time = time_service_begins - arrival_time

# Time in system
time_in_system = wait_time + service_time

# Server utilization
utilization = total_busy_time / total_simulation_time
```

### The Loop Structure

```python
for each customer:
    1. Generate inter-arrival time (exponential)
    2. Calculate arrival time
    3. Generate service time (uniform)
    4. Calculate when service begins (queue logic!)
    5. Calculate wait time
    6. Calculate departure time
    7. Store results
    8. Update state for next customer
```

### Parameters to Experiment With

- `MEAN_INTERARRIVAL_TIME`: ↓ = more customers = longer waits
- `MAX_SERVICE_TIME`: ↑ = slower service = longer waits
- `NUM_CUSTOMERS`: ↑ = more stable results

### Expected Utilization

```
avg_service_time = (MIN_SERVICE_TIME + MAX_SERVICE_TIME) / 2
utilization ≈ avg_service_time / MEAN_INTERARRIVAL_TIME
```

If utilization > 95%, expect very long waits!

---

## Quick FAQ

**Q: Do I need to install anything?**
A: No! Uses only Python standard library (`random`, `math`).

**Q: What Python version?**
A: Python 3.6+ (any modern Python).

**Q: How long does the lab take?**
A: 10 min (run & experiment) to 3 hours (complete guide + extensions).

**Q: Can I use this for my own projects?**
A: Yes! The code is educational. Adapt it for your queuing problems.

**Q: Why not use SimPy from the start?**
A: Because you need to understand what SimPy does for you! Lab 2 will use SimPy.

---

## Ready? Let's Simulate!

**Option 1 (Fast)**: Run `python coffee_shop_sim.py` right now!

**Option 2 (Learn by Doing)**: Open `coffee_shop_sim_starter.py` and start coding!

**Option 3 (Deep Dive)**: Read `LAB_GUIDE.md` for comprehensive understanding!

**No matter which path you choose, you're about to discover the power of simulation modeling.**

**Happy simulating!** ☕📊
