# Lab 1: Building Your First Simulation in Python

**Course**: IDS 6742 - Real-Time Simulation Modeling for Digital Twins
**Prerequisites**: Basic Python programming (variables, loops, functions)
**Estimated Time**: 2-3 hours

---

## Table of Contents

1. [Lab Objective](#lab-objective)
2. [The Scenario](#the-scenario)
3. [Theoretical Foundation](#theoretical-foundation)
4. [Phase 1: Setup](#phase-1-setup)
5. [Phase 2: Building the Simulation](#phase-2-building-the-simulation)
6. [Phase 3: Calculating Metrics](#phase-3-calculating-metrics)
7. [Phase 4: Analysis & Experiments](#phase-4-analysis--experiments)
8. [Deliverables](#deliverables)
9. [Extension Challenges](#extension-challenges)

---

## Lab Objective

In this foundational lab, you will build a **discrete-event simulation** of a single-server queuing system from scratch using basic Python. This will teach you the fundamental concepts of simulation before we introduce simulation frameworks like SimPy in later labs.

### What You'll Learn

- How to use loops and variables to drive a simulation forward in time
- How to generate random arrivals and service times using probability distributions
- How to calculate queue performance metrics (wait time, server utilization, etc.)
- The relationship between server utilization and customer wait times
- The variability inherent in stochastic simulations

### Why Start Without a Framework?

By coding the simulation logic manually, you'll understand exactly what happens "under the hood" when you use frameworks like SimPy later. You'll see that:
- Simulations are just loops that process events
- State variables track the system's condition over time
- Random numbers drive the stochastic behavior
- Performance metrics are calculated from collected data

---

## The Scenario: The One-Person Coffee Stand

You're analyzing a small coffee stand with a **single barista**. Customers arrive randomly throughout the day, and each customer requires a random amount of service time. Your goal is to answer questions like:

- How long do customers wait on average?
- What's the probability a customer has to wait at all?
- How busy is the barista (server utilization)?
- What happens if customers arrive faster? Or if service is slower?

### System Components

In queuing theory terminology:

- **Entities**: Customers (the things flowing through the system)
- **Resource**: Barista (the server providing service)
- **Queue**: The line of waiting customers
- **Arrival Process**: Customers arrive randomly (Poisson process)
- **Service Process**: Service times are random (Uniform distribution)

### Key Assumptions

1. **Single server**: Only one barista
2. **FIFO discipline**: First In, First Out (first customer in line is served first)
3. **Infinite queue**: No limit on how many customers can wait
4. **Independent service**: Service time doesn't depend on queue length
5. **No balking or reneging**: Customers don't leave if the line is long

---

## Theoretical Foundation

### Random Arrival Times: The Poisson Process

In many real-world systems, arrivals are **random and memoryless**:
- Customers arrive independently
- The time between arrivals (inter-arrival time) follows an **exponential distribution**

**Exponential Distribution Formula**:
```
inter-arrival time = -ln(U) × mean_interarrival_time
```
where `U` is a uniform random number between 0 and 1 from `random.random()`

**Why exponential?**
- Models truly random arrivals (like customers walking into a shop)
- Memoryless property: past arrivals don't affect future arrivals
- Easy to generate with Python's `random` module

### Random Service Times: The Uniform Distribution

For this lab, we assume service times are uniformly distributed between a min and max:
```
service_time = random.uniform(MIN_SERVICE_TIME, MAX_SERVICE_TIME)
```

**Why uniform?**
- Simple starting point (all values equally likely within range)
- Later labs will use more realistic distributions (normal, triangular, etc.)

### The Core Queue Logic

The magic happens in one line:
```python
time_service_begins = max(arrival_time, time_server_is_free)
```

**What this means**:
- If customer arrives and server is free (`arrival_time ≥ time_server_is_free`):
  - Service begins immediately
  - Wait time = 0
- If customer arrives and server is busy (`arrival_time < time_server_is_free`):
  - Customer must wait until server is free
  - Wait time = `time_server_is_free - arrival_time`

### Key Performance Indicators (KPIs)

1. **Average Wait Time**: Mean time customers spend in queue
   ```
   avg_wait = sum(all_wait_times) / num_customers
   ```

2. **Probability of Waiting**: Fraction of customers who had to wait
   ```
   prob_wait = (customers_with_wait > 0) / total_customers
   ```

3. **Server Utilization**: Fraction of time server was busy
   ```
   utilization = (total_busy_time) / (total_simulation_time)
   ```

4. **Average Time in System**: Mean time from arrival to departure
   ```
   avg_time_in_system = wait_time + service_time
   ```

---

## Phase 1: Setup

### Step 1: Create Your Project

```bash
mkdir lab1-coffee-shop-sim
cd lab1-coffee-shop-sim
```

### Step 2: Create Python File

Create a file named `coffee_shop_sim.py`

### Step 3: Import Libraries

```python
import random
import math
```

**Why these libraries?**
- `random`: Generate random numbers (uniform and exponential distributions)
- `math`: Mathematical functions (logarithm for exponential distribution)

### Step 4: Define Input Parameters

```python
# --- Input Parameters ---
MEAN_INTERARRIVAL_TIME = 3.0  # Average minutes between arrivals
MIN_SERVICE_TIME = 2.0        # Minimum service time (minutes)
MAX_SERVICE_TIME = 5.0        # Maximum service time (minutes)
NUM_CUSTOMERS_TO_SIMULATE = 100
```

**Design Principle**: Put all parameters at the top for easy experimentation.

---

## Phase 2: Building the Simulation

### Step 1: Initialize State Variables

Before the loop, set up variables to track the system's state:

```python
# --- State Variables ---
time_of_previous_arrival = 0.0  # When did the last customer arrive?
time_server_is_free = 0.0       # When will the server be free?

# --- Result Storage ---
wait_times = []
times_in_system = []
server_idle_periods = []
```

**Why these variables?**
- `time_of_previous_arrival`: Needed to calculate next arrival time
- `time_server_is_free`: Needed to determine if customer waits
- Lists: Store metrics for all customers for later analysis

### Step 2: The Main Simulation Loop

Each iteration of this loop represents **one customer's complete journey** through the system:

```python
for customer_num in range(1, NUM_CUSTOMERS_TO_SIMULATE + 1):
    # 1. Generate inter-arrival time and calculate arrival time
    interarrival_time = -math.log(random.random()) * MEAN_INTERARRIVAL_TIME
    arrival_time = time_of_previous_arrival + interarrival_time

    # 2. Generate service time
    service_time = random.uniform(MIN_SERVICE_TIME, MAX_SERVICE_TIME)

    # 3. Determine when service begins (THE QUEUE LOGIC!)
    time_service_begins = max(arrival_time, time_server_is_free)

    # 4. Calculate metrics
    wait_in_queue = time_service_begins - arrival_time
    time_service_ends = time_service_begins + service_time
    time_in_system = time_service_ends - arrival_time
    server_idle_time = time_service_begins - time_server_is_free

    # 5. Store results
    wait_times.append(wait_in_queue)
    times_in_system.append(time_in_system)
    server_idle_periods.append(server_idle_time)

    # 6. Update state for next customer
    time_of_previous_arrival = arrival_time
    time_server_is_free = time_service_ends
```

### Understanding the Loop Logic

Let's trace through Customer #1 and Customer #2:

**Customer #1**:
- `time_of_previous_arrival = 0.0` (simulation starts at time 0)
- `interarrival_time = 2.5` (random)
- `arrival_time = 0.0 + 2.5 = 2.5`
- `service_time = 3.2` (random between 2 and 5)
- `time_server_is_free = 0.0` (server idle at start)
- `time_service_begins = max(2.5, 0.0) = 2.5` (no wait!)
- `wait_in_queue = 2.5 - 2.5 = 0`
- `time_service_ends = 2.5 + 3.2 = 5.7`
- Update: `time_server_is_free = 5.7`

**Customer #2**:
- `time_of_previous_arrival = 2.5`
- `interarrival_time = 1.8` (random)
- `arrival_time = 2.5 + 1.8 = 4.3`
- `service_time = 4.1` (random)
- `time_server_is_free = 5.7` (server busy with Customer #1)
- `time_service_begins = max(4.3, 5.7) = 5.7` (must wait!)
- `wait_in_queue = 5.7 - 4.3 = 1.4` minutes
- `time_service_ends = 5.7 + 4.1 = 9.8`
- Update: `time_server_is_free = 9.8`

**See the pattern?** Each customer's experience depends on the state left by the previous customer!

---

## Phase 3: Calculating Metrics

After the loop completes, calculate the final KPIs:

```python
# Average Wait Time
avg_wait_time = sum(wait_times) / len(wait_times)

# Probability of Waiting
customers_who_waited = len([w for w in wait_times if w > 0])
prob_wait = customers_who_waited / NUM_CUSTOMERS_TO_SIMULATE

# Server Utilization
total_simulation_time = time_server_is_free  # When last customer leaves
total_idle_time = sum(server_idle_periods)
total_busy_time = total_simulation_time - total_idle_time
server_utilization = total_busy_time / total_simulation_time

# Other metrics
avg_time_in_system = sum(times_in_system) / len(times_in_system)
max_wait_time = max(wait_times)
```

### Display Results

```python
print("\n" + "="*50)
print("           SIMULATION RESULTS")
print("="*50)
print(f"\nPerformance Metrics:")
print(f"  Average Wait Time:      {avg_wait_time:.2f} minutes")
print(f"  Maximum Wait Time:      {max_wait_time:.2f} minutes")
print(f"  Probability of Waiting: {prob_wait:.2%}")
print(f"  Server Utilization:     {server_utilization:.2%}")
print(f"  Average Time in System: {avg_time_in_system:.2f} minutes")
print("="*50)
```

---

## Phase 4: Analysis & Experiments

Run your simulation and answer the following questions by modifying parameters and observing results.

### Experiment 1: Stochastic Variability

**Task**: Run the simulation 10 times without changing any parameters.

**Questions**:
1. Does the Average Wait Time change between runs? By how much?
2. Does the Server Utilization stay approximately constant? Why or why not?
3. What does this tell you about making business decisions based on a single simulation run?

**Expected Observation**: You'll see variability in the results because the simulation uses random numbers. This is called **stochastic variability** or **sampling error**.

**Implication**: To get reliable results, you need to:
- Run multiple replications (we'll learn this in later labs)
- Use longer simulation runs (more customers)
- Calculate confidence intervals (advanced topic)

### Experiment 2: Increased Arrival Rate

**Task**: Change `MEAN_INTERARRIVAL_TIME` from 3.0 to 2.0 (customers arrive more frequently).

**Questions**:
1. What happens to Average Wait Time?
2. What happens to Server Utilization?
3. What happens to Probability of Waiting?
4. Why do all three metrics change the way they do?

**Expected Observation**:
- Wait time **increases dramatically**
- Server utilization **increases**
- More customers wait

**Explanation**: The barista is busier (higher utilization), so arriving customers are more likely to find the server busy, leading to longer waits.

### Experiment 3: Slower Service

**Task**: Reset interarrival time to 3.0. Change `MAX_SERVICE_TIME` from 5.0 to 8.0.

**Questions**:
1. What happens to Average Wait Time?
2. What happens to Server Utilization?
3. Calculate the average service time: `(MIN + MAX) / 2`. How does this compare to the mean interarrival time?

**Expected Observation**:
- Wait time **increases**
- Server utilization **increases**
- Average service time: `(2 + 8) / 2 = 5` minutes
- Mean interarrival time: 3 minutes
- Service time > arrival time means server can't keep up!

### Experiment 4: The Utilization-Wait Time Relationship

**Task**: Run the simulation with different `MEAN_INTERARRIVAL_TIME` values to achieve different utilization levels:

| Mean Interarrival | Expected Utilization | Avg Wait Time |
|-------------------|----------------------|---------------|
| 10.0              | ~35%                 | ?             |
| 5.0               | ~70%                 | ?             |
| 4.0               | ~87.5%               | ?             |
| 3.5               | ~100%                | ?             |
| 3.0               | >100% (unstable!)    | ?             |

**To calculate expected utilization**:
```
Average service time = (MIN_SERVICE_TIME + MAX_SERVICE_TIME) / 2 = (2 + 5) / 2 = 3.5

Expected utilization = avg_service_time / mean_interarrival_time
                     = 3.5 / mean_interarrival_time
```

**Questions**:
1. Plot utilization (x-axis) vs. average wait time (y-axis). What shape is the curve?
2. What happens when utilization approaches 100%?
3. At what utilization level do waits become "unacceptable" (e.g., > 5 minutes)?

**Expected Observation**:
- Wait time increases **exponentially** as utilization approaches 100%
- This is a fundamental property of queuing systems!
- Most businesses target 70-80% utilization to balance efficiency and service quality

### Experiment 5: Number of Customers

**Task**: Run the simulation with `NUM_CUSTOMERS = 50`, `100`, `500`, `1000`.

**Questions**:
1. Do the KPIs stabilize as you simulate more customers?
2. How many customers do you need to get consistent results?

**Expected Observation**: More customers → more stable results (Law of Large Numbers)

---

## Deliverables

Submit the following:

### 1. Your Python Script (`coffee_shop_sim.py`)

Include comments explaining:
- What each section does
- The queue logic (the `max()` function)
- How metrics are calculated

### 2. Experiment Results Document

For each experiment (1-5), report:
- Parameter values used
- Output KPIs observed
- Answers to the questions
- Your insights/observations

**Format**: PDF or Markdown document

### 3. Analysis Summary

Write a brief (1-2 page) summary answering:

**Question 1**: Based on Experiment 4, if you were the coffee shop owner, what server utilization would you target? Why?

**Question 2**: The current system has mean interarrival time = 3.0 and service time range [2, 5]. Customers complain that waits are too long. What are three ways to reduce wait times? (Hint: Think about the parameters you can change)

**Question 3**: This simulation makes several simplifying assumptions (single server, FIFO, no customer abandonment). How might real-world coffee shops differ? What would you need to change in the simulation to model a real shop more accurately?

---

## Extension Challenges

Once you've completed the basic lab, try these extensions:

### Challenge 1: Add Visualization

Use `matplotlib` to plot:
- Histogram of wait times
- Time-series plot of server utilization over time
- Scatter plot of arrival time vs. wait time

```python
import matplotlib.pyplot as plt

plt.hist(wait_times, bins=20, edgecolor='black')
plt.xlabel('Wait Time (minutes)')
plt.ylabel('Number of Customers')
plt.title('Distribution of Customer Wait Times')
plt.show()
```

### Challenge 2: Warm-Up Period

The first few customers often see no wait (server is idle at start). This biases the results.

Modify your code to:
- Simulate 1000 customers
- Discard the first 100 customers (warm-up period)
- Calculate KPIs only from customers 101-1000

Compare results with and without warm-up.

### Challenge 3: Multiple Replications

Run the simulation 10 times (10 replications) and:
- Calculate the **mean** of the average wait times across all replications
- Calculate the **standard deviation** of the average wait times
- Report results as: `mean ± std_dev`

This gives you a confidence interval!

### Challenge 4: Peak Hours

Model a coffee shop with time-varying arrivals:
- Morning rush (7-9 AM): Mean interarrival = 1.5 minutes
- Mid-morning (9-11 AM): Mean interarrival = 4.0 minutes
- Lunch rush (11 AM-1 PM): Mean interarrival = 2.0 minutes

Modify the code to change `MEAN_INTERARRIVAL_TIME` based on simulation clock time.

### Challenge 5: Two Servers

What if the coffee shop hires a second barista?

Modify the code to:
- Track two servers (`server1_free_time`, `server2_free_time`)
- Assign arriving customer to whichever server is free first
- Calculate utilization for each server

How much does adding a second server reduce wait times?

---

## Common Mistakes & Troubleshooting

### Mistake 1: Forgetting to Update State Variables

**Symptom**: All customers wait the same amount

**Cause**: Not updating `time_server_is_free` at the end of the loop

**Fix**: Ensure you have:
```python
time_server_is_free = time_service_ends
```

### Mistake 2: Using `min()` Instead of `max()`

**Symptom**: Negative wait times!

**Cause**: Using `min(arrival_time, time_server_is_free)` instead of `max()`

**Fix**: Service begins at the **later** of arrival or when server is free:
```python
time_service_begins = max(arrival_time, time_server_is_free)
```

### Mistake 3: Division by Zero

**Symptom**: Error when calculating probabilities

**Cause**: Using `NUM_CUSTOMERS_TO_SIMULATE = 0` or empty lists

**Fix**: Ensure `NUM_CUSTOMERS > 0` and check list lengths before dividing

### Mistake 4: Exponential Distribution Error

**Symptom**: `ValueError: math domain error` (logarithm of negative number)

**Cause**: `random.random()` returned exactly 0.0 (rare but possible)

**Fix**: Use `random.random()` which returns (0, 1) exclusive, or add a small epsilon:
```python
interarrival_time = -math.log(random.random() + 1e-10) * MEAN_INTERARRIVAL_TIME
```

### Mistake 5: Utilization > 100%

**Symptom**: Server utilization reported as > 100%

**Cause**: System is **unstable** (arrivals faster than service)

**Interpretation**: This is not a bug! If `avg_service_time > mean_interarrival_time`, the queue grows without bound. The simulation will eventually crash or run forever.

**Fix**: Increase interarrival time or decrease service time to achieve stable system.

---

## Key Takeaways

By completing this lab, you've learned:

1. **Simulations are loops**: Each iteration processes one event (customer arrival)

2. **State variables track the system**: Past events affect future events via state

3. **Random numbers drive stochasticity**: Exponential for arrivals, Uniform for service

4. **Queue logic is simple but powerful**: `max(arrival, server_free)` captures waiting

5. **Metrics come from collected data**: Store results, then calculate statistics

6. **Stochastic simulations vary**: Run multiple replications for robust results

7. **Utilization drives performance**: As utilization → 100%, wait times explode

8. **Simulation reveals non-obvious insights**: Like the exponential wait time vs. utilization relationship

---

## Next Steps

In **Lab 2**, we'll rebuild this same coffee shop simulation using **SimPy**, a discrete-event simulation framework. You'll see how SimPy handles:
- Event scheduling (no manual loop!)
- Resource management (automatic queue handling)
- Process-based modeling (customer "processes")

By building it manually first, you'll appreciate what SimPy does for you and understand the underlying mechanics.

---

## Additional Resources

### Queuing Theory Background

- **Little's Law**: `L = λ × W` (average queue length = arrival rate × average wait time)
- **M/M/1 Queue**: Markovian arrivals, Markovian service, 1 server (analytical formulas exist!)
- **Kingman's Formula**: Approximates wait time based on utilization and variability

### Python Learning Resources

- Python `random` module documentation: https://docs.python.org/3/library/random.html
- Python `math` module documentation: https://docs.python.org/3/library/math.html

### Simulation Textbooks

- Law, A.M. (2015). *Simulation Modeling and Analysis* (5th ed.). McGraw-Hill.
- Banks, J., et al. (2010). *Discrete-Event System Simulation* (5th ed.). Prentice Hall.

---

**Congratulations on building your first simulation!**

You've taken a critical first step in understanding how to model complex systems. The skills you've learned here—thinking in terms of events, states, and random processes—will serve you throughout this course and in real-world modeling projects.

Now run your simulation, experiment with the parameters, and see what insights you can uncover about this simple coffee shop. The same principles apply whether you're modeling a coffee stand or a Digital Twin of a smart factory.

**Happy simulating!**
