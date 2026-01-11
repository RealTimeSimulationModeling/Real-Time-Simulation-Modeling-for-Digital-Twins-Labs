# Quick Start Guide - Lab 3: Warehouse AGVs

## 60-Second Setup

```bash
# 1. Navigate to the lab directory
cd Lab3-Warehouse-AGVs

# 2. Install dependencies
pip install mesa

# 3. Run the simulation
python warehouse_agv_model.py

# 4. Open browser to:
http://127.0.0.1:8521

# 5. Click "Start" button
```

## What You'll See

A warehouse floor with:
- ⬛ Black walls (boundaries)
- 🟤 Brown shelves (obstacles)
- ⚡ Gold charging stations
- 💗 Pink dropoff points (D)
- Colored circles = AGVs (moving robots)

## AGV Color Code

Watch the AGV colors - they reveal the agent's state:

- 🟢 **Green** = Idle (waiting for work)
- 🔵 **Light Blue** = Going to pickup
- 🔵 **Blue** = Delivering package
- 🟡 **Yellow** = Charging battery
- 🔴 **RED** = Blocked/Waiting ⚠️ **THIS IS EMERGENCE!**

## What to Look For (Emergence!)

### 1. Traffic Jams (The Main Event!)
**Look for**: Multiple RED AGVs clustered together
- **Where**: Near pink dropoff points
- **Why**: Each AGV follows simple rules, but congestion emerges
- **Cool fact**: This wasn't programmed - it just happens!

### 2. Charging Queues
**Look for**: Yellow AGVs gathering at gold stations
- Batteries drain as AGVs work
- Multiple AGVs may need charging at once
- Natural queue forms without coordination

### 3. Bottlenecks
**Look for**: Lines of waiting AGVs in corridors
- Narrow passages between shelves
- Bidirectional traffic creates conflicts
- Complex patterns from simple "wait if blocked" rule

## Interactive Controls

- **Slider**: Adjust number of AGVs (5-25)
  - Try 5 AGVs: Smooth operation, little congestion
  - Try 25 AGVs: Chaos! Congestion everywhere!

- **Step Button**: Advance one tick at a time
  - Good for analyzing specific situations

- **Reset**: Start over with new random setup

## Quick Experiments

### Experiment 1: Find the Congestion Point
1. Start with 5 AGVs - smooth operation
2. Increase slider to 10 - occasional blocking
3. Increase to 15 - regular congestion appears
4. Increase to 25 - gridlock!

**Question**: What's the optimal number for this warehouse?

### Experiment 2: Watch Battery Management
1. Find a green (idle) AGV
2. Watch it turn blue when it gets a task
3. See battery % decrease as it moves
4. Watch it turn yellow and head to charging when low
5. See it return to green when fully charged

### Experiment 3: Identify Bottleneck Locations
1. Run simulation for 100+ steps
2. Note where RED AGVs cluster most often
3. These are your bottleneck locations!
4. In a real warehouse, you'd widen these corridors

## Common Issues

**Problem**: Port already in use
```python
# Edit warehouse_agv_model.py, line ~590
server.port = 8522  # Change to different port
```

**Problem**: All AGVs are yellow (charging)
- This can happen! They all ran low on battery simultaneously
- Wait for them to charge and turn green
- Or reset the simulation

**Problem**: Browser shows blank screen
- Refresh the page
- Check if JavaScript is enabled
- Try Chrome or Firefox

## Understanding What You're Seeing

This is **Agent-Based Modeling (ABM)**:
- Each colored circle is an autonomous agent
- Each agent has simple rules (follow path, avoid collisions)
- Complex traffic patterns **emerge** from these simple rules
- No central controller - it's all distributed!

**The RED AGVs are the key**: They show where the simple rules create unexpected system behavior (congestion). This emergence wasn't programmed - it arose naturally!

## Next Steps

1. Read the full README.md for detailed explanations
2. Study the code to understand the state machine
3. Try the exercises in README.md
4. Modify parameters and observe changes

## File Structure

```
Lab3-Warehouse-AGVs/
├── README.md                    # Full documentation
├── QUICKSTART.md                # This file
├── requirements.txt             # Dependencies
└── warehouse_agv_model.py       # Main simulation
```

## Key Takeaway

**Simple Rules → Complex Behavior**

Each AGV knows:
- Follow my path
- Wait if blocked
- Charge when battery low

From just these 3 rules, you get:
- Traffic jams
- Queuing behavior
- Bottleneck formation
- Oscillating traffic patterns

This is the power of Agent-Based Modeling!

---

**Have fun watching emergence in action! 🚛🤖**
