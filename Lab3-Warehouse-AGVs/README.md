# Lab 3: Twinning a Warehouse with AGVs

## Overview

This lab implements an **Agent-Based Model (ABM)** of a warehouse populated by Autonomous Guided Vehicles (AGVs) using the Mesa framework. The model demonstrates how complex emergent behaviors (like traffic congestion) arise from simple individual agent rules and prepares the foundation for Digital Twin integration.

## Learning Objectives

- Understand core Agent-Based Modeling concepts
- Implement autonomous agents with state machines
- Observe emergent phenomena from local interactions
- Implement spatial pathfinding algorithms (A*)
- Create visual simulations for analysis
- Design instrumentation hooks for Digital Twin systems

## ABM Concepts Demonstrated

### 1. Agents with State and Rules
**AGV Agents** have:
- **Internal State**: Battery level, current task, position, state machine status
- **Behavior Rules**: State-dependent actions (idle, moving, charging, delivering)
- **Autonomy**: Each AGV makes its own decisions based on local information

### 2. Agent-Environment Interaction
- **Spatial Environment**: 2D grid representing warehouse floor
- **Pathfinding**: AGVs use A* algorithm to navigate around obstacles
- **Environmental Constraints**: Walls and shelves create navigation challenges

### 3. Agent-Agent Interaction
- **Sensing**: AGVs detect other AGVs in adjacent cells
- **Collision Avoidance**: AGVs wait if target cell is occupied
- **Competition**: Multiple AGVs compete for charging stations and pathways

### 4. Emergence
**Complex patterns emerge from simple rules:**
- **Traffic Congestion**: AGVs cluster and queue at bottlenecks
- **Deadlocks**: AGVs can block each other in narrow passages
- **Self-Organization**: Queue formation at charging stations and dropoff points
- **System-Level Patterns**: Traffic flows that weren't explicitly programmed

### 5. Spatial Representation
- **MultiGrid**: Allows multiple agents per cell (AGV + charging station)
- **2D Topology**: Models physical warehouse layout
- **Non-Torus**: Bounded environment with walls

## Files in This Lab

### `warehouse_agv_model.py`
Complete ABM implementation with Mesa visualization

**Components**:
- **A* Pathfinding Algorithm**: Intelligent navigation
- **Static Agents**: Walls, Shelves, Charging Stations, Dropoff Points
- **Dynamic AGV Agents**: State machine with 5 states
- **Warehouse Model**: Environment manager and scheduler
- **Visualization Server**: Browser-based interactive display
- **Digital Twin Hooks**: Methods for external control

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. Install required packages:
```bash
pip install -r requirements.txt
```

Or install Mesa directly:
```bash
pip install mesa
```

2. Run the simulation:
```bash
python warehouse_agv_model.py
```

3. Open your browser to:
```
http://127.0.0.1:8521
```

4. Click "Start" to begin the simulation

## How to Use the Visualization

### Controls
- **Start**: Begin continuous simulation
- **Stop**: Pause the simulation
- **Step**: Advance one time step
- **Reset**: Restart with new random initialization
- **Slider**: Adjust number of AGVs (5-25)

### Color Legend

**AGV States** (colored circles):
- 🟢 **Green** = IDLE (waiting for task assignment)
- 🔵 **Light Blue** = MOVING_TO_PICKUP (en route to pickup)
- 🔵 **Blue** = DELIVERING (en route to dropoff)
- 🟡 **Yellow** = CHARGING (replenishing battery)
- 🔴 **RED** = WAITING (blocked by another AGV) **← EMERGENCE!**

**Environment** (background):
- ⬛ **Black** = Walls (non-navigable)
- 🟤 **Brown** = Shelves (obstacles)
- 🟡 **Gold ⚡** = Charging Stations
- 💗 **Pink D** = Dropoff Points

### Battery Display
Each AGV shows its battery percentage as text inside the circle.

## What to Observe (Emergence!)

### 1. Traffic Congestion at Dropoff Points
**Watch for**: Clusters of RED AGVs near pink dropoff points

**Why it happens**:
- Multiple AGVs independently choose the same destination
- Collision avoidance causes queuing
- First-come-first-served naturally emerges
- **This is NOT programmed** - it emerges from local rules!

### 2. Bottleneck Formation
**Watch for**: Lines of waiting AGVs in narrow corridors between shelves

**Why it happens**:
- Limited pathways force AGVs through the same routes
- Bidirectional traffic creates conflicts
- Simple "wait if blocked" rule creates complex traffic patterns

### 3. Charging Station Queues
**Watch for**: Multiple YELLOW AGVs at or near gold charging stations

**Why it happens**:
- AGVs independently monitor their own battery
- Multiple AGVs may reach low battery simultaneously
- Natural queueing emerges from resource scarcity

### 4. Deadlock Scenarios
**Watch for**: AGVs permanently stuck (rare but possible)

**Why it happens**:
- Circular dependencies in tight spaces
- Each AGV waits for another to move
- Demonstrates limitations of purely reactive agents

## Four-Phase Implementation

### Phase 1: Environment and Static Agents

**Components**:
- `WallAgent`: Non-navigable barriers
- `ShelfAgent`: Storage obstacles
- `ChargingStationAgent`: Battery replenishment points
- `DropoffPointAgent`: Delivery destinations
- `WarehouseModel`: Environment manager
- `astar()`: Pathfinding algorithm

**Key Concepts**: Spatial environment, obstacle-based navigation

### Phase 2: Dynamic AGV Agent

**Components**:
- `AGVAgent` class with state machine
- 5 behavioral states (IDLE, MOVING_TO_PICKUP, DELIVERING, CHARGING, WAITING)
- Battery management system
- Task execution logic
- Collision avoidance

**Key Concepts**: Autonomous agents, state machines, sensing

### Phase 3: Visualization and Emergence

**Components**:
- `agent_portrayal()` function
- Mesa CanvasGrid
- ModularServer
- State-dependent coloring

**Key Concepts**: Visual analysis, emergent pattern observation

### Phase 4: Instrumentation for Twinning

**Components**:
- `override_position()`: External position control
- `assign_external_task()`: External task assignment

**Key Concepts**: Digital Twin hooks, bidirectional data flow

## AGV State Machine

```
        ┌─────────┐
        │  IDLE   │◄────────────┐
        └────┬────┘             │
             │                  │
    Task Assigned          Task Complete
             │                  │
             ▼                  │
    ┌────────────────┐          │
    │ MOVING_TO_     │          │
    │   PICKUP       │          │
    └────────┬───────┘          │
             │                  │
      Reached Pickup            │
             │                  │
             ▼                  │
    ┌────────────────┐          │
    │  DELIVERING    ├──────────┘
    └────────┬───────┘
             │
      If Blocked
             │
             ▼
    ┌────────────────┐
    │    WAITING     │ (Emergence!)
    └────────────────┘

    (At any time, low battery → CHARGING state)
```

## Configuration Parameters

### Model Parameters
```python
width = 30              # Grid width
height = 30             # Grid height
num_agvs = 15          # Number of AGVs (adjustable via slider)
```

### AGV Parameters
```python
battery_level = 100.0              # Initial battery %
battery_drain_rate = 0.5           # % per move
battery_charge_rate = 5.0          # % per step at station
low_battery_threshold = 20.0       # % trigger for charging
```

### Task Parameters
```python
initial_tasks = 30                 # Tasks in queue at start
min_task_queue = 10               # Regenerate when below this
task_batch_size = 5               # Tasks generated at once
```

## Exercises and Extensions

### Beginner
1. **Adjust AGV Count**: Use the slider to change from 5 to 25 AGVs
   - Observe how congestion increases with more AGVs
   - Find the optimal number for smooth operation

2. **Modify Battery Parameters**: Change drain/charge rates
   - Faster drain → more charging trips
   - Slower charging → longer queues at stations

3. **Alter Warehouse Layout**: Edit the layout string
   - Add more corridors to reduce congestion
   - Remove charging stations to increase competition

### Intermediate
4. **Add Priority Tasks**: Implement "urgent" deliveries
   - Give certain AGVs priority in pathways
   - Observe how this affects overall system

5. **Implement Communication**: Allow AGVs to signal their destinations
   - AGVs could avoid choosing same dropoff point
   - Compare emergent vs. coordinated behavior

6. **Add Performance Metrics**: Track and display:
   - Average delivery time
   - Total distance traveled
   - Charging station utilization

### Advanced
7. **Implement Deadlock Detection**: Add logic to detect and resolve deadlocks
   - AGVs could back up when stuck too long
   - Compare system efficiency with/without this

8. **Adaptive Pathfinding**: Implement dynamic path costs
   - Heavily-used paths become "more expensive"
   - AGVs naturally load-balance

9. **Learning Agents**: Implement Q-learning
   - AGVs learn optimal paths over time
   - Compare performance with/without learning

10. **Multi-Agent Coordination**: Implement negotiation protocols
    - AGVs negotiate who waits when paths conflict
    - Study coordination vs. pure autonomy trade-offs

## Digital Twin Concepts

This lab demonstrates Digital Twin foundations:

### 1. Virtual Representation
The `WarehouseModel` and `AGVAgent` classes represent physical warehouse and AGVs

### 2. State Synchronization
The hook methods allow external data to update simulation state:
```python
agv.override_position((10, 15))  # Update from GPS/sensors
agv.assign_external_task(task)   # Update from WMS
```

### 3. Predictive Capability
The simulation can:
- Predict where congestion will occur
- Forecast battery depletion times
- Test "what-if" scenarios (e.g., adding more AGVs)

### 4. Real-Time Monitoring
The visualization provides real-time insight into:
- Current system state
- Emerging problems (congestion, deadlocks)
- Resource utilization

## Pathfinding Algorithm

The lab implements **A* (A-Star)** pathfinding:

### How It Works
1. **Frontier**: Priority queue of positions to explore
2. **Cost Function**: f(n) = g(n) + h(n)
   - g(n) = actual cost from start
   - h(n) = heuristic estimate to goal (Manhattan distance)
3. **Obstacle Avoidance**: Walls and shelves marked as non-navigable
4. **Optimal Paths**: Guarantees shortest path if one exists

### Why A*?
- **Efficient**: Faster than breadth-first search
- **Optimal**: Finds shortest paths
- **Flexible**: Easy to modify cost functions
- **Industry Standard**: Used in robotics and games

## Troubleshooting

### Mesa Not Installed
```bash
pip install mesa
```

### Server Won't Start
- Check if port 8521 is already in use
- Try changing `server.port = 8521` to another port (e.g., 8522)

### No AGVs Moving
- Check if they're all CHARGING (yellow)
- Verify tasks are being generated (check console output)
- Reset the simulation

### Browser Shows Blank Grid
- Ensure JavaScript is enabled
- Try a different browser (Chrome/Firefox recommended)
- Check browser console for errors (F12)

### Simulation Runs Too Slow
- Reduce number of AGVs via slider
- Smaller warehouse dimensions (modify layout)
- Disable battery percentage text in portrayal

### Simulation Runs Too Fast
- Use "Step" button instead of "Start"
- Add `time.sleep()` in model.step() for slower execution

## Understanding Emergence

**Emergence** is when system-level patterns arise that aren't explicitly programmed into individual agents.

### In This Lab:
**Individual AGV Rules** (Simple):
- Follow path to destination
- If next cell occupied, wait
- Charge when battery low

**Emergent System Patterns** (Complex):
- Traffic congestion at popular destinations
- Queue formation at resources
- Bottleneck creation in narrow passages
- Load balancing across charging stations
- Oscillating traffic flows

**Key Insight**: You cannot predict these patterns by analyzing one AGV in isolation. They only appear when multiple AGVs interact in a spatial environment. This is the power of ABM!

## Comparison: ABM vs DES

This lab uses ABM; Lab 2 used DES. Key differences:

| Aspect | DES (Lab 2) | ABM (Lab 3) |
|--------|-------------|-------------|
| **Focus** | Process flow | Individual entities |
| **Space** | Implicit | Explicit (grid) |
| **Interaction** | Queue-based | Spatial proximity |
| **Emergence** | Limited | Central focus |
| **Best For** | Process optimization | Spatial/social systems |

Both are valuable for Digital Twins - choose based on your system!

## References

- **Mesa Documentation**: https://mesa.readthedocs.io/
- **Agent-Based Modeling**: Wilensky, U. & Rand, W. "An Introduction to Agent-Based Modeling"
- **Pathfinding**: Hart, P. et al. "A Formal Basis for the Heuristic Determination of Minimum Cost Paths" (A* algorithm)
- **Digital Twins**: Grieves, M. & Vickers, J. "Digital Twin: Mitigating Unpredictable, Undesirable Emergent Behavior"

## Author Notes

This lab is designed to teach:
- Agent-Based Modeling fundamentals
- Mesa framework usage
- Emergent phenomena observation
- Spatial simulation techniques
- Digital Twin instrumentation

The code is extensively commented to connect implementation with ABM theory. Pay special attention to how simple rules create complex behaviors!

## Next Steps

After completing this lab:
1. Experiment with different AGV counts and observe emergence
2. Modify warehouse layout to test different configurations
3. Implement one or more extension exercises
4. Consider how to connect this to real warehouse data
5. Think about combining ABM (Lab 3) with DES (Lab 2) for hybrid models

Happy modeling!
