# Lab 8: Hybrid Factory Model - Quick Start Guide

## What This Lab Does

Integrates **three modeling paradigms** into a single factory simulation:

- **DES (Discrete Event Simulation)**: Production process flow
- **ABM (Agent-Based Modeling)**: Autonomous maintenance technicians
- **SD (System Dynamics)**: Continuous machine health degradation

Shows how events in one paradigm trigger actions in another, creating realistic emergent behavior.

---

## The 30-Second Concept

**The System**:
- Parts arrive and wait in queue for machine
- Machine processes parts but gradually wears down
- When health drops too low, machine breaks
- Technicians repair the machine, restoring health
- Production resumes

**The Paradigms**:
- **DES**: Models part arrivals, queue, processing (discrete events)
- **SD**: Models health degradation over time (continuous)
- **ABM**: Models technicians' decisions and actions (autonomous agents)

**The Magic**: Each paradigm does what it's best at, but they work together seamlessly!

---

## Quick Setup

```bash
pip install -r requirements.txt
```

That's it!

---

## Running the Simulation

```bash
python hybrid_factory_simulation.py
```

### Expected Output (Console)

```
======================================================================
HYBRID FACTORY SIMULATION
======================================================================
Simulation time: 480 minutes
Number of technicians: 2
Health threshold: 20.0
======================================================================

[DES] Part(1) arrived at t=3.2 (Queue: 1)
[DES] Part(1) service started at t=3.2 (duration: 3.4 min)
[DES] Part(1) completed at t=6.6 (Total: 1)
[DES] Part(2) arrived at t=7.1 (Queue: 1)
...

[SD] Machine health critical! (18.7) at t=127.5
[DES] Machine blocked - production halted
[ABM] Dispatching Technician 0 to repair
  [ABM] Technician 0 started repairing at t=127.5
  [ABM] Technician 0 finished repair at t=142.3
  [DES] Machine unblocked and back in service

...

======================================================================
SIMULATION STATISTICS
======================================================================
Parts created:    98
Parts completed:  82
Parts in queue:   16

Average wait time:    8.43 minutes
Average service time: 3.12 minutes

Machine breakdowns:   3
Average downtime:     14.87 minutes
Availability:         90.7%
======================================================================
```

### Expected Output (Visualization)

A six-panel plot opens showing:

1. **Machine Health (SD)**: Oscillating line with degradation and repair cycles
2. **Machine State (DES)**: Green (busy) and red (broken) periods
3. **Queue Length (DES)**: Spikes during breakdowns
4. **Cumulative Production (DES)**: Stepwise increasing line with flat plateaus during breakdowns
5. **Technician States (ABM)**: Idle vs. repairing counts
6. **Integrated View**: All three paradigms overlaid and normalized

---

## Understanding the Flow

### The Integration Cycle

```
1. Machine processes parts (DES)
   ↓
2. Health degrades while busy (SD)
   ↓
3. Health drops below 20 (SD threshold)
   ↓
4. Machine breaks! (SD → DES)
   ↓
5. Idle technician dispatched (DES → ABM)
   ↓
6. Technician repairs machine (ABM → SD)
   ↓
7. Health restored to 100 (SD)
   ↓
8. Machine unblocked (ABM → DES)
   ↓
9. Production resumes (DES)
   ↓
Back to step 1
```

### Key Observations

**Watch the console output carefully**:

- `[DES]` messages: Part flow events (arrival, service start/end)
- `[SD]` messages: Health threshold crossed (breakdown trigger)
- `[ABM]` messages: Technician actions (dispatch, start repair, finish repair)

**Notice the timing**:
- Parts keep arriving even when machine is broken → Queue builds up
- Repair takes ~15 minutes → Backlog must be cleared after
- Health degrades faster when machine is busy → Trade-off!

---

## Understanding the Plots

### Plot 1: Machine Health (SD)

**What it shows**: Continuous health value over time

**Pattern to observe**:
- Starts at 100
- **Gradual decline** (steeper slope when machine is busy)
- **Sharp drop** below red threshold line at 20
- **Rapid recovery** during repair (steep upward slope)
- **Oscillating sawtooth pattern**

**Why it matters**: The SD model creates a wear-and-tear cycle that drives everything else.

### Plot 2: Machine State (DES)

**What it shows**: Machine activity

**Colors**:
- **Green**: Machine processing parts
- **Red**: Machine broken (downtime)
- **White**: Machine idle (no parts)

**Why it matters**: Breakdowns interrupt production, creating delays.

### Plot 3: Queue Length (DES)

**What it shows**: Parts waiting for machine

**Pattern to observe**:
- **Sudden spikes** when machine breaks (parts pile up)
- **Gradual decline** after repair (backlog cleared)
- Queue length during breakdown ≈ arrival rate × downtime

**Why it matters**: Shows the cascade effect of health degradation on production.

### Plot 4: Cumulative Production (DES)

**What it shows**: Total parts completed over time

**Pattern to observe**:
- **Stepwise increase** (discrete completions)
- **Flat plateaus** during breakdowns (no production)
- Final count < arrival count (parts still in queue)

**Why it matters**: Overall throughput limited by machine availability.

### Plot 5: Technician States (ABM)

**What it shows**: Number of technicians in each state

**Usual pattern**:
- 2 idle, 0 repairing (technicians waiting)

**During breakdown**:
- 1 idle, 1 repairing (one dispatched)

**Why it matters**: Shows agent response to events from other paradigms.

### Plot 6: Integrated View (All Paradigms)

**What it shows**: All three paradigms overlaid (normalized 0-1)

**Key correlations**:
- When **health (blue)** drops → **queue (orange)** rises
- **Production (green)** plateaus when health is low
- **Red shading** shows breakdown periods

**Why it matters**: Visualizes the tight coupling between paradigms.

---

## Quick Experiments

### Experiment 1: More Technicians

In `hybrid_factory_simulation.py`:
```python
NUM_TECHNICIANS = 4  # Was 2
```

**Expected result**:
- Faster repairs (multiple technicians available)
- Less downtime
- Higher throughput
- Diminishing returns (only 1 machine to repair!)

### Experiment 2: Faster Degradation

```python
DEGRADATION_RATE_BUSY = 0.3  # Was 0.15 (2x faster)
```

**Expected result**:
- More frequent breakdowns
- Longer queues
- Lower availability
- Technicians busier

### Experiment 3: Higher Health Threshold

```python
HEALTH_THRESHOLD = 40.0  # Was 20.0
```

**Expected result**:
- Preventive "maintenance" before critical failure
- More frequent but shorter repairs
- Trade-off: More interruptions vs. faster recovery

### Experiment 4: Slower Repairs

```python
REPAIR_TIME_MEAN = 30.0  # Was 15.0 (2x longer)
```

**Expected result**:
- Longer downtime per breakdown
- Massive queue build-up
- Lower throughput
- May need more technicians!

---

## Common Patterns to Notice

### Pattern 1: Cyclic Breakdowns

Breakdowns happen in a **predictable cycle**:
- Machine processes ~60-80 parts
- Health degrades to threshold
- Breakdown occurs
- Repair restores health
- Cycle repeats

**Why**: SD degradation + DES workload + ABM repair create a feedback loop.

### Pattern 2: Queue Spikes

Queue **surges** during breakdowns:
- Parts arrive at ~5 min intervals
- If breakdown lasts 15 min, ~3 parts accumulate
- After repair, machine clears backlog

**Why**: DES arrivals continue regardless of SD/ABM state.

### Pattern 3: Availability vs. Throughput

Higher health threshold:
- ✅ Higher availability (less time broken)
- ❌ More frequent interruptions
- ? Net throughput: Depends on repair speed!

**Why**: Hybrid dynamics create non-obvious trade-offs.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No module named 'simpy'" | Run `pip install simpy` |
| "No module named 'mesa'" | Run `pip install mesa>=3.0` |
| Plot doesn't appear | Add `plt.show()` at end of script |
| Simulation takes too long | Reduce `SIM_TIME` to 120 minutes |
| No breakdowns occur | Increase `DEGRADATION_RATE_BUSY` |

---

## What Makes This "Hybrid"?

### If We Only Used DES

```python
# Awkward: Continuous health as discrete checks
def check_health():
    if random.random() < 0.05:  # 5% chance per minute
        machine_breaks()
```

**Problem**: Loses causality (why did it break NOW?), can't model gradual wear.

### If We Only Used SD

```python
# Awkward: Parts as averaged flow
parts_per_minute = 0.2
completion_rate = 0.3 * (1 - machine_broken)
```

**Problem**: Loses discrete parts, individual wait times, queue dynamics.

### If We Only Used ABM

```python
# Awkward: Parts as agents, machine as agent
class PartAgent:
    def step(self):
        if machine.available:
            machine.process(self)
```

**Problem**: Every part is an agent (inefficient), no queueing semantics, unnatural.

### Hybrid Approach

```python
# Natural: Each component uses best paradigm
DES: part_arrival() → queue → machine.process()
SD: health -= degradation_rate * dt
ABM: technician.repair() if machine.broken
```

**Benefit**: Each component is simple and natural. Complexity emerges from interactions!

---

## Key Metrics

**Typical Results** (8-hour shift):

| Metric | Value | Meaning |
|--------|-------|---------|
| Parts created | ~98 | Arrivals at ~5 min intervals |
| Parts completed | ~82 | Actual production |
| Efficiency | 84% | Completed / Created |
| Breakdowns | 3 | Depends on degradation rate |
| Avg downtime | ~15 min | Depends on repair time |
| Availability | 90%+ | Productive time / Total time |

**Bottleneck Analysis**:
- If queue always > 0: Machine capacity limited (add machine)
- If availability < 85%: Too many breakdowns (add technicians or preventive maintenance)
- If technicians always idle: Over-capacity (reduce technicians)

---

## Next Steps

1. **Read full README.md** for:
   - Detailed architecture explanation
   - Line-by-line code walkthrough
   - Extension ideas (preventive maintenance, multiple machines, learning technicians)
   - Real-world applications

2. **Try experiments above**:
   - Observe how changing one parameter affects all paradigms
   - Find optimal technician count
   - Discover non-obvious trade-offs

3. **Extend the model**:
   - Add part priorities (urgent vs. normal)
   - Implement preventive maintenance
   - Add multiple machines with shared repair crew
   - Model spare parts inventory

4. **Apply to your domain**:
   - Healthcare: Patient flow + staff fatigue + doctor agents
   - Logistics: Vehicle flow + fuel levels + driver agents
   - IT: Request flow + server health + admin agents

---

## Summary

You've run a **hybrid simulation** that integrates:

✅ **DES (SimPy)**: Discrete part arrivals, queueing, processing
✅ **SD (Custom)**: Continuous machine health degradation
✅ **ABM (Mesa)**: Autonomous technician agents

**Key Integration Points**:
- SD health threshold → DES machine block
- DES breakdown → ABM technician dispatch
- ABM repair → SD health restoration
- ABM completion → DES unblock

**Emergent Behavior**: Cyclic breakdowns, queue surges, throughput oscillation - none exist in isolation, all emerge from paradigm interactions!

**Why It Matters**: Real systems are hybrid. Mastering multi-paradigm modeling lets you capture complexity that single approaches miss.

**Congratulations!** You now understand how to build, run, and analyze hybrid simulations.

---

For detailed explanations, see **README.md**.
