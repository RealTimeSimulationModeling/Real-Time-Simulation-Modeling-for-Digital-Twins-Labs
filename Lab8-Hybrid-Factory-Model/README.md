# Lab 8: Hybrid Factory Model - Integrating DES, ABM, and SD

## Overview

This lab demonstrates **hybrid simulation modeling** - the integration of multiple modeling paradigms into a single unified model. You'll build a factory simulation that combines:

- **Discrete Event Simulation (DES)**: Production process flow
- **Agent-Based Modeling (ABM)**: Autonomous maintenance technicians
- **System Dynamics (SD)**: Continuous machine health degradation

This represents real-world complexity where different aspects of a system are best modeled with different techniques, but must work together seamlessly.

### The Integration Challenge

Real systems exhibit behaviors that span multiple paradigms:

- **Discrete events**: Parts arrive, machines break, repairs complete
- **Continuous processes**: Machine health gradually degrades over time
- **Autonomous agents**: Technicians make independent decisions

Using a single paradigm forces compromises. **Hybrid modeling** lets each component use the most natural representation.

### Learning Objectives

By the end of this lab, you will understand:

1. **Why Hybrid Modeling Matters**
   - Limitations of single-paradigm models
   - When to use DES vs. ABM vs. SD
   - Benefits of integration

2. **Cross-Paradigm Integration**
   - SD → DES: Health threshold triggers machine block
   - DES → ABM: Machine failure dispatches technician
   - ABM → SD: Repair increases machine health
   - ABM → DES: Repair completion unblocks machine

3. **Implementation Techniques**
   - Shared state management
   - Event-driven coordination
   - Time synchronization across paradigms

4. **Analysis of Hybrid Systems**
   - Emergent behavior from interactions
   - Bottleneck identification
   - Trade-off analysis

---

## System Architecture

### The Factory Model

```
┌─────────────────────────────────────────────────────────────┐
│                     FACTORY MODEL                           │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │  DES: Production Process (SimPy)                  │    │
│  │                                                    │    │
│  │  Source → Queue → Machine → Sink                  │    │
│  │   (Parts arrive)  (Wait)  (Process) (Complete)    │    │
│  └───────────────────────────────────────────────────┘    │
│                          │                                  │
│                          │ Machine state                    │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────┐    │
│  │  SD: Machine Health (Continuous)                  │    │
│  │                                                    │    │
│  │  Health ◄─── degradation_rate (busy/idle)        │    │
│  │  Health ◄─── repair_rate (from technicians)      │    │
│  │                                                    │    │
│  │  if Health < threshold → TRIGGER BREAKDOWN        │    │
│  └───────────────────────────────────────────────────┘    │
│                          │                                  │
│                          │ Repair request                   │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────┐    │
│  │  ABM: Maintenance Technicians (Mesa)              │    │
│  │                                                    │    │
│  │  Technician States:                               │    │
│  │    Idle → MovingToMachine → Repairing → Idle     │    │
│  │                                                    │    │
│  │  Actions:                                         │    │
│  │    - Receive repair request                       │    │
│  │    - Travel to machine                            │    │
│  │    - Restore health (→ SD)                        │    │
│  │    - Unblock machine (→ DES)                      │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

**1. SD → DES (Health threshold triggers production halt)**
```python
if machine_health < HEALTH_THRESHOLD:
    machine_is_broken = True  # Block DES machine
```

**2. DES → ABM (Production halt requests repair)**
```python
if machine_is_broken:
    idle_technician = find_idle_technician()
    idle_technician.request_repair()  # Dispatch agent
```

**3. ABM → SD (Technician repairs machine)**
```python
while repairing:
    machine_health += REPAIR_RATE * dt  # Increase SD stock
```

**4. ABM → DES (Repair completes, resume production)**
```python
machine_is_broken = False  # Unblock DES machine
machine_health = 100  # Reset SD stock
```

---

## Implementation Details

### 1. DES Component (SimPy)

**Part Entity**:
```python
class Part:
    def __init__(self, arrival_time):
        self.id = Part.part_counter
        self.arrival_time = arrival_time
```

**Production Process**:
```python
def part_source(self):
    while True:
        part = Part(self.env.now)
        self.queue.append(part)
        self.env.process(self.machine_service(part))
        yield self.env.timeout(interarrival_time)

def machine_service(self, part):
    with self.machine.request() as request:
        yield request
        # Process part
        yield self.env.timeout(service_time)
        self.parts_completed += 1
```

**Key Features**:
- SimPy Environment for event scheduling
- Resource (machine) with capacity = 1
- Queue for waiting parts
- Service process with random processing times

**Challenge**: Must handle interruptions from machine breakdowns!

```python
while processing:
    if self.machine_is_broken:
        # Service interrupted!
        self.queue.insert(0, part)  # Return to front of queue
        yield self.env.timeout(1.0)  # Wait for repair
```

### 2. SD Component (Custom)

**State Variables**:
```python
machine_health = 100.0  # Stock
```

**Flow Equations**:
```python
def update_machine_health(self, dt):
    # Degradation (outflow)
    if machine_is_busy:
        degradation = DEGRADATION_RATE_BUSY * dt  # 0.15/min
    else:
        degradation = DEGRADATION_RATE_IDLE * dt  # 0.02/min

    # Repair (inflow)
    repair = 0.0
    for tech in technicians:
        if tech.is_repairing():
            repair += REPAIR_RATE * dt  # 10.0/min

    # Stock equation
    machine_health += repair - degradation
    machine_health = max(0, min(100, machine_health))
```

**Threshold Logic**:
```python
def check_health_threshold(self):
    if machine_health < HEALTH_THRESHOLD and not machine_is_broken:
        # Trigger breakdown (SD → DES → ABM cascade)
        machine_is_broken = True
        dispatch_technician()
```

**Integration**: Runs on a fixed time step (0.5 minutes) within SimPy's event loop.

### 3. ABM Component (Mesa)

**Technician Agent with Statechart**:
```python
class TechnicianAgent(mesa.Agent):
    def __init__(self, model, technician_id):
        super().__init__(model)
        self.state = TechnicianState.IDLE

    def request_repair(self):
        # Idle → MovingToMachine
        self.state = TechnicianState.MOVING_TO_MACHINE
        self.arrive_at_machine()

    def arrive_at_machine(self):
        # MovingToMachine → Repairing
        self.state = TechnicianState.REPAIRING
        self.repair_start_time = self.model.env.now
        self.repair_duration = random.gauss(15, 5)

    def step(self):
        if self.state == TechnicianState.REPAIRING:
            if self.model.env.now >= self.repair_start_time + self.repair_duration:
                self.finish_repair()

    def finish_repair(self):
        # Repairing → Idle
        # Restore machine (ABM → SD)
        self.model.machine_health = 100
        # Unblock production (ABM → DES)
        self.model.machine_is_broken = False
        self.state = TechnicianState.IDLE
```

**Agent States**:
- **Idle**: Waiting at base, available for dispatch
- **MovingToMachine**: Traveling to machine (instantaneous in this model)
- **Repairing**: Actively repairing, increasing machine health

**Decision Logic**: Agents are dispatched on a first-available basis when machine breaks.

### 4. Model Orchestration

The `FactoryModel` class coordinates all three paradigms:

```python
class FactoryModel:
    def __init__(self):
        # DES
        self.env = simpy.Environment()
        self.machine = simpy.Resource(self.env, capacity=1)
        self.queue = []

        # SD
        self.machine_health = 100.0
        self.machine_is_broken = False

        # ABM
        self.technicians = [TechnicianAgent(self, i) for i in range(2)]

    def monitor_process(self):
        """Background process integrating SD and ABM"""
        dt = 0.5  # Time step
        while True:
            # Update SD
            self.update_machine_health(dt)
            self.check_health_threshold()

            # Step ABM agents
            for tech in self.technicians:
                tech.step()

            yield self.env.timeout(dt)

    def run(self, until=480):
        self.env.process(self.part_source())
        self.env.process(self.monitor_process())
        self.env.run(until=until)
```

**Time Synchronization**:
- SimPy controls master time
- SD updated on fixed time step (0.5 min)
- ABM agents stepped synchronously with SD

---

## Running the Lab

### Prerequisites

```bash
pip install -r requirements.txt
```

### Execution

```bash
python hybrid_factory_simulation.py
```

### Expected Output

**Console**:
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
Average total time:   11.55 minutes

Machine breakdowns:   3
Average downtime:     14.87 minutes
Total downtime:       44.61 minutes
Availability:         90.7%
======================================================================
```

**Visualization**: Six-panel plot showing:
1. Machine health over time (SD)
2. Machine state (busy/broken) over time (DES)
3. Queue length over time (DES)
4. Cumulative production over time (DES)
5. Technician states over time (ABM)
6. Integrated normalized view (all three paradigms)

---

## Understanding the Results

### Panel 1: Machine Health (SD)

**What to observe**:
- Health starts at 100
- Gradual degradation (steeper when machine is busy)
- Sharp drops below red threshold line (20)
- Rapid recovery during repair (steep increase)
- Oscillating pattern: degrade → break → repair → recover

**Key insight**: The SD model creates a **wear-and-tear cycle** that drives the overall system dynamics.

### Panel 2: Machine State (DES)

**What to observe**:
- Green areas: Machine processing parts
- Red areas: Machine broken (downtime)
- White areas: Machine idle (no parts in queue)

**Key insight**: Breakdowns **interrupt** the discrete production process, creating delays that propagate through the queue.

### Panel 3: Queue Length (DES)

**What to observe**:
- Queue builds up when machine is busy
- **Sudden spikes** when machine breaks (parts accumulate)
- Gradual decline after repair as backlog is cleared

**Key insight**: The **interaction** between continuous degradation (SD) and discrete arrivals (DES) creates complex queueing behavior.

### Panel 4: Cumulative Production (DES)

**What to observe**:
- Stepwise increase (discrete part completions)
- **Flat plateaus** during machine breakdowns
- Slope = production rate

**Key insight**: Total output is **limited by machine availability**, which depends on health (SD) and repair speed (ABM).

### Panel 5: Technician States (ABM)

**What to observe**:
- Usually: 2 idle, 0 repairing (technicians waiting)
- During breakdown: 1 idle, 1 repairing (technician dispatched)
- Repair events align with health recovery in Panel 1

**Key insight**: Technicians are **reactive agents** that respond to events from other paradigms (SD health threshold).

### Panel 6: Integrated View

**What to observe**:
- **Inverse correlation**: When health (blue) drops, queue (orange) rises
- Production (green) plateaus when health is low
- Red shading shows breakdown periods linking all effects

**Key insight**: The three paradigms are **tightly coupled** - changes in one immediately affect the others.

---

## Hybrid Modeling Insights

### Why Not Just Use One Paradigm?

**Option 1: Pure DES**
- ✅ Natural for part flow, queue, machine
- ❌ Awkward for continuous health degradation
- ❌ Would require "checking events" every time step
- ❌ Technician behavior would be procedural, not autonomous

**Option 2: Pure ABM**
- ✅ Natural for technicians
- ❌ Part flow would need to be agent-based (inefficient)
- ❌ Continuous health degradation unnatural
- ❌ No built-in queueing semantics

**Option 3: Pure SD**
- ✅ Natural for health degradation
- ❌ Cannot represent discrete parts
- ❌ Cannot represent individual technicians
- ❌ Queue would be averaged (lose discrete events)

**Hybrid Approach**:
- ✅ Each component uses the **most natural paradigm**
- ✅ Integration points are **explicit and clear**
- ✅ Model matches **conceptual understanding** of system
- ✅ Easier to validate, explain, and extend

### Emergent Behavior

The hybrid model exhibits behaviors that emerge from paradigm interactions:

1. **Cyclic Breakdowns**: SD degradation rate depends on DES machine utilization
2. **Backlog Surges**: DES queue responds to SD health thresholds
3. **Repair Prioritization**: ABM technicians affect SD health, which unblocks DES
4. **Throughput Oscillation**: Production rate varies with health-driven availability

None of these behaviors exist in isolation - they emerge from **cross-paradigm coupling**.

---

## Extension Ideas

### 1. Preventive Maintenance (ABM → SD)

Add scheduled maintenance before breakdown:

```python
def preventive_maintenance_check(self):
    if machine_health < 50 and not machine_is_broken:
        # Schedule preventive maintenance
        idle_tech = find_idle_technician()
        idle_tech.request_maintenance()  # Different from reactive repair
```

**Analysis**: Does preventive maintenance reduce total downtime? What's the optimal threshold?

### 2. Priority Queue (DES Enhancement)

Implement priority for urgent parts:

```python
class Part:
    def __init__(self, arrival_time, priority=1):
        self.priority = priority

# Sort queue by priority
self.queue.sort(key=lambda p: p.priority, reverse=True)
```

**Analysis**: How does breakdown affect high-priority vs. low-priority parts?

### 3. Variable Degradation (SD → DES Coupling)

Make degradation depend on part complexity:

```python
class Part:
    def __init__(self, complexity):
        self.complexity = complexity  # 1.0 = standard, 2.0 = complex

degradation = DEGRADATION_RATE_BUSY * part.complexity * dt
```

**Analysis**: Should complex parts be rationed when health is low?

### 4. Learning Technicians (ABM Enhancement)

Technicians get faster with experience:

```python
class TechnicianAgent:
    def __init__(self):
        self.repairs_completed = 0
        self.skill_level = 1.0

    def finish_repair(self):
        self.repairs_completed += 1
        self.skill_level = min(2.0, 1.0 + 0.1 * self.repairs_completed)

    def get_repair_time(self):
        return REPAIR_TIME_MEAN / self.skill_level
```

**Analysis**: How does learning curve affect long-term availability?

### 5. Multiple Machines (DES Expansion)

Add parallel machines with shared repair crew:

```python
self.machine_1 = simpy.Resource(self.env, capacity=1)
self.machine_2 = simpy.Resource(self.env, capacity=1)
self.health_1 = 100.0
self.health_2 = 100.0

# Technicians must choose which machine to repair
def dispatch_technician(self):
    # Which machine has lower health?
    if self.health_1 < self.health_2:
        return self.machine_1
    else:
        return self.machine_2
```

**Analysis**: Is 2 technicians sufficient for 2 machines? What if degradation rates differ?

### 6. Spare Parts Inventory (DES + SD)

Repairs require spare parts from inventory:

```python
self.spare_parts_stock = 10  # Initial inventory

def finish_repair(self):
    if self.model.spare_parts_stock > 0:
        self.model.spare_parts_stock -= 1
        # Complete repair
    else:
        # Wait for parts to arrive
        yield self.env.timeout(reorder_delay)
```

**Analysis**: What's the optimal spare parts inventory level?

---

## Real-World Applications

Hybrid modeling is essential for complex systems across industries:

### Manufacturing (This Lab's Domain)

- **Production lines**: DES for part flow, SD for tool wear, ABM for operators
- **Quality control**: DES for inspection, SD for defect accumulation, ABM for inspectors
- **Supply chain**: DES for shipments, SD for inventory levels, ABM for suppliers

### Healthcare

- **Emergency department**: DES for patient flow, SD for staff fatigue, ABM for doctors
- **Epidemic spread**: DES for events (testing, treatment), SD for disease dynamics, ABM for individuals
- **Hospital operations**: DES for procedures, SD for resource consumption, ABM for patients

### Transportation

- **Air traffic control**: DES for flights, SD for fuel, ABM for aircraft with autonomous decisions
- **Logistics**: DES for deliveries, SD for vehicle wear, ABM for drivers
- **Public transit**: DES for schedule, SD for ridership trends, ABM for passengers

### Energy

- **Smart grids**: DES for events (switching), SD for power flow, ABM for prosumers
- **Oil refinery**: DES for batch processing, SD for tank levels, ABM for operators
- **Renewable integration**: DES for grid events, SD for battery charge, ABM for homes

### Military

- **Combat simulation**: DES for engagements, SD for ammunition/fuel, ABM for units
- **Logistics**: DES for supply missions, SD for stockpiles, ABM for commanders
- **Command & control**: DES for orders, SD for morale, ABM for soldiers

---

## Common Pitfalls

### 1. Time Step Mismatch

**Problem**: SD time step too large misses fast DES events

**Solution**:
```python
dt = min(mean_interarrival_time, mean_service_time) / 10
```

### 2. State Inconsistency

**Problem**: DES thinks machine is available, but SD knows it's broken

**Solution**: Single source of truth
```python
# GOOD: Single variable
self.machine_is_broken

# BAD: Multiple copies
self.des_machine_broken
self.sd_machine_broken
```

### 3. Circular Dependencies

**Problem**: A depends on B depends on A in same time step

**Solution**: Update in defined order
```python
# 1. Update SD (machine health)
# 2. Check thresholds (may break machine)
# 3. Dispatch ABM agents
# 4. Step ABM agents (may repair machine)
```

### 4. Ignoring Delays

**Problem**: Repair happens instantly, unrealistic

**Solution**: Model travel time and repair duration
```python
def request_repair(self):
    yield self.env.timeout(travel_time)  # Travel to machine
    yield self.env.timeout(repair_duration)  # Perform repair
```

---

## Key Takeaways

1. **Hybrid Models Match Reality**
   - Real systems exhibit discrete events, continuous processes, and autonomous agents
   - Using one paradigm forces unnatural representations
   - Hybrid models align with conceptual understanding

2. **Integration is the Challenge**
   - Each paradigm has its own time representation
   - Must synchronize state across components
   - Integration points must be explicit and bidirectional

3. **Emergent Behavior is Powerful**
   - Complex behavior arises from simple rules in each paradigm
   - Interactions create feedback loops
   - Cannot predict system behavior from components alone

4. **Choose Paradigms Purposefully**
   - DES: Discrete events, queueing, processes
   - ABM: Heterogeneous entities, autonomous decisions, spatial behavior
   - SD: Continuous flows, feedback loops, policies

5. **Validation is Critical**
   - Each paradigm must be validated independently
   - Integration points must be tested
   - Emergent behavior must match domain expertise

---

## References

### Hybrid Modeling Theory
- Zeigler, B.P. et al. (2000). "Theory of Modeling and Simulation"
- Siebers, P. & Aickelin, U. (2008). "Introduction to Multi-Agent Simulation"
- Vangheluwe, H. (2000). "Multi-Formalism Modelling and Simulation"

### Tools and Frameworks
- SimPy Documentation: https://simpy.readthedocs.io/
- Mesa Documentation: https://mesa.readthedocs.io/
- AnyLogic (Commercial): Example of GUI-based hybrid modeling

### Applications
- Tako, A.A. & Robinson, S. (2012). "The application of discrete event simulation and system dynamics in the logistics and supply chain context"
- Chahal, K. & Eldabi, T. (2008). "Applicability of hybrid simulation to different modes of governance in UK healthcare"
- Brailsford, S. et al. (2018). "Hybrid simulation modelling in operational research: A state-of-the-art review"

---

## Summary

This lab integrated **three modeling paradigms** into a unified factory simulation:

- **DES (SimPy)**: Part arrival, queueing, machine processing
- **SD (Custom)**: Continuous machine health degradation and repair
- **ABM (Mesa)**: Autonomous technician agents with statechart behavior

You learned:
- ✅ When each paradigm is most appropriate
- ✅ How to implement cross-paradigm interactions
- ✅ How to synchronize time across paradigms
- ✅ How emergent behavior arises from integration
- ✅ How to visualize and analyze hybrid models

**Key Integration Points**:
1. SD health threshold → DES machine block
2. DES breakdown → ABM technician dispatch
3. ABM repair → SD health restoration
4. ABM completion → DES machine unblock

This **cyclic interaction** creates realistic system behavior that no single paradigm could capture.

**Congratulations on mastering hybrid simulation modeling!** You now have the skills to model complex systems that combine discrete events, continuous dynamics, and autonomous agents.
