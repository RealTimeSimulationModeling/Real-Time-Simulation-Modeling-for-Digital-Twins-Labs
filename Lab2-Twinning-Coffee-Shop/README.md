# Lab 2: Twinning a Coffee Shop

## Overview

This lab implements a **discrete-event simulation (DES)** of a coffee shop using Python and SimPy, demonstrating the foundational concepts of digital twins. The implementation progresses through three phases, each building upon the previous one to create a simulation that can be dynamically controlled in real-time.

## Learning Objectives

- Understand the core components of discrete-event simulation (DES)
- Implement the **Process-Interaction Worldview** in SimPy
- Model stochastic systems using probability distributions
- Instrument a simulation for dynamic parameter updates
- Simulate real-time data feeds controlling a digital twin

## DES Concepts Demonstrated

### Entities
- **Customer**: Individual entities moving through the system
- Each customer has a unique ID and follows a defined lifecycle

### Resources
- **Barista**: Limited resources that customers must seize to receive service
- Implemented using `simpy.Store` for dynamic capacity management

### Queues
- Implicit queuing when all baristas are busy
- Customers automatically wait until a barista becomes available

### Stochastic Events
- **Arrivals**: Exponential distribution (memoryless, Poisson process)
- **Service Times**: Triangular distribution (min, mode, max)

### Process-Interaction Worldview
The simulation is modeled from the customer's perspective:
1. Customer arrives at shop
2. Customer requests a barista (waits if none available)
3. Customer receives service (time delay)
4. Customer releases the barista
5. Customer leaves the system

## Files in This Lab

### 1. `coffee_shop_simulation.py`
**Standard DES Implementation**

This is the main educational script demonstrating all three phases:
- Phase 1: Foundational DES model
- Phase 2: Instrumentation for dynamic updates
- Phase 3: Control panel simulation

**Note**: The simulation runs very quickly (milliseconds), so control panel events may not be visible in the output. This version is best for understanding the code structure and DES concepts.

**Run with**:
```bash
python coffee_shop_simulation.py
```

### 2. `coffee_shop_simulation_realtime.py`
**Real-Time DES Implementation**

Enhanced version using `simpy.rt.RealtimeEnvironment` that synchronizes simulation time with wall-clock time. This makes control panel interventions observable.

**Key Features**:
- Simulation runs at 1:10 speed ratio (1 real second = 10 simulation minutes)
- Control events are visible as they happen
- Better demonstrates digital twin behavior

**Run with**:
```bash
python coffee_shop_simulation_realtime.py
```

**Expected Runtime**: ~20 seconds (runs 200 simulation minutes)

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. Install required packages:
```bash
pip install -r requirements.txt
```

Or install SimPy directly:
```bash
pip install simpy
```

2. Run either simulation:
```bash
# Fast version (educational)
python coffee_shop_simulation.py

# Real-time version (demonstration)
python coffee_shop_simulation_realtime.py
```

## Three-Phase Implementation

### Phase 1: Foundational DES Model

**Objective**: Create a standard stochastic simulation

**Components**:
- `CoffeeShop` class encapsulating the simulation
- `customer()` process defining entity lifecycle
- `setup()` process generating customer arrivals
- Data collection for statistics

**Key Code Elements**:
```python
# Customer process (Process-Interaction Worldview)
def customer(self, customer_id):
    arrival_time = self.env.now
    barista = yield self.barista_store.get()  # Seize resource
    # ... service ...
    yield self.barista_store.put(barista)     # Release resource

# Customer generator with exponential arrivals
def setup(self):
    while True:
        interarrival = random.expovariate(1.0 / self.mean_interarrival)
        yield self.env.timeout(interarrival)
        self.env.process(self.customer(customer_id))
```

### Phase 2: Instrumentation for Twinning

**Objective**: Enable dynamic parameter changes during simulation

**Instrumentation Methods**:

1. **`set_arrival_rate(new_mean_interarrival)`**
   - Dynamically adjusts customer arrival rate
   - Simulates changing foot traffic patterns

2. **`add_barista()`**
   - Adds a new barista resource during simulation
   - Simulates staff arriving for their shift

3. **`remove_barista()`**
   - Removes a barista resource (after current service)
   - Simulates staff going on break

**Key Design Choice**: Using `simpy.Store` instead of `simpy.Resource` allows dynamic capacity changes. Each barista is an object that can be added or removed from the store.

### Phase 3: Simulating Real-Time Connection

**Objective**: Create external control process mimicking real-world data feeds

**Implementation**:
- Separate Python thread running the `control_panel()` function
- Thread operates on wall-clock time (real seconds)
- Simulation operates on simulation time (simulated minutes)
- Demonstrates asynchronous digital twin architecture

**Control Panel Timeline** (real-time version):
- **t=3s**: Lunch rush starts → Increase arrival rate
- **t=6s**: New barista arrives → Add resource
- **t=10s**: Lunch rush ends → Decrease arrival rate
- **t=14s**: Barista break → Remove resource

## Configuration Parameters

Both scripts use these configurable parameters:

```python
RANDOM_SEED = 42                    # Reproducibility
NUM_BARISTAS = 2                    # Initial staff count
SIM_TIME = 100                      # Simulation duration (minutes)
INITIAL_MEAN_INTERARRIVAL = 5       # Mean time between arrivals

# Service time distribution (triangular)
SERVICE_TIME_MIN = 2                # Minimum service time
SERVICE_TIME_MODE = 3               # Most likely service time
SERVICE_TIME_MAX = 5                # Maximum service time
```

**Real-time version adds**:
```python
REALTIME_SCALE = 10                 # 1 real second = 10 sim minutes
```

## Understanding the Output

### Event Logs
```
[  5.10] Customer   1 | ARRIVES
[  5.10] Customer   1 | STARTS SERVICE (waited 0.00 min) with Barista_1
[  8.01] Customer   1 | LEAVES (service took 2.91 min)
```

- **Time**: Current simulation time (minutes)
- **Customer ID**: Unique identifier
- **Event**: ARRIVES, STARTS SERVICE, LEAVES
- **Metrics**: Wait time, service time, barista assignment

### Control Events
```
********************************************************************************
[15.23] CONTROL EVENT | Arrival rate changed: 5.00 min -> 2.00 min
********************************************************************************
```

- **Control events** are marked with asterisks
- Show dynamic parameter changes during simulation

### Final Statistics
```
Simulation Time:          100 minutes
Customers Served:         27
Final Barista Count:      2

Waiting Time Statistics:
  Average Wait Time:      0.25 minutes
  Maximum Wait Time:      2.53 minutes
  Minimum Wait Time:      0.00 minutes
```

## Exercises and Extensions

### Beginner
1. Change the number of initial baristas and observe impact on wait times
2. Modify arrival rate to simulate different time periods
3. Adjust service time distribution parameters

### Intermediate
4. Add data collection for barista utilization rates
5. Implement a "VIP customer" entity with priority queuing
6. Add visualization of queue length over time

### Advanced
7. Implement multiple service stations (order, payment, pickup)
8. Add resource breakdowns (barista unavailable for random periods)
9. Create a GUI dashboard for real-time monitoring
10. Connect to actual IoT sensors for real data feeds

## Digital Twin Concepts

This lab demonstrates key digital twin principles:

1. **Virtual Representation**: The `CoffeeShop` class models the physical coffee shop
2. **Bi-directional Data Flow**: Control panel sends updates; simulation returns statistics
3. **Real-Time Synchronization**: Real-time version synchronizes with wall-clock time
4. **Dynamic Updates**: Parameters change during runtime based on external events
5. **Predictive Capability**: Can forecast wait times under different scenarios

## Troubleshooting

### SimPy Not Installed
```bash
pip install simpy
```

### Control Events Not Visible (Standard Version)
This is expected - the simulation runs too fast. Use the real-time version:
```bash
python coffee_shop_simulation_realtime.py
```

### Simulation Runs Too Slow (Real-Time Version)
Adjust the `REALTIME_SCALE` parameter or reduce `SIM_TIME`:
```python
REALTIME_SCALE = 20  # Faster: 1 second = 20 sim minutes
SIM_TIME = 100       # Shorter simulation
```

## References

- **SimPy Documentation**: https://simpy.readthedocs.io/
- **Discrete Event Simulation**: Banks, J. et al. "Discrete-Event System Simulation"
- **Digital Twins**: Grieves, M. "Digital Twin: Manufacturing Excellence through Virtual Factory Replication"

## Author Notes

This lab is designed for educational purposes to teach:
- Discrete-event simulation fundamentals
- SimPy library usage
- Digital twin concepts
- Real-time control systems

The code is extensively commented to connect implementation details with theoretical DES concepts.
