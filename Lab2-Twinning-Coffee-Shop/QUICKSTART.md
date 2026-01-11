# Quick Start Guide - Lab 2: Coffee Shop Digital Twin

## 60-Second Setup

```bash
# 1. Navigate to the lab directory
cd Lab2-Twinning-Coffee-Shop

# 2. Install dependencies
pip install simpy

# 3. Run the simulation (choose one):

# Fast version - for code study
python coffee_shop_simulation.py

# Real-time version - for demonstration
python coffee_shop_simulation_realtime.py
```

## What You'll See

### Standard Version (Fast)
- Completes in < 1 second
- Shows all customer arrivals, service, and departures
- Displays final statistics
- Best for understanding code structure

### Real-Time Version (Recommended for Demo)
- Runs for ~20 seconds
- **Shows control panel events in real-time**:
  - Lunch rush starts (arrival rate increases)
  - New barista added
  - Lunch rush ends (arrival rate decreases)
  - Barista goes on break
- Best for demonstrating digital twin concepts

## Expected Output (Real-Time Version)

```
[  5.10] Customer   1 | ARRIVES
[  5.10] Customer   1 | STARTS SERVICE (waited 0.00 min) with Barista_1
...

[CONTROL PANEL] >>> Real-world event: LUNCH RUSH DETECTED! <<<

********************************************************************************
[ 29.68] CONTROL EVENT | Arrival rate changed: 5.00 min -> 2.00 min
********************************************************************************

...

[CONTROL PANEL] >>> Real-world event: ADDITIONAL STAFF AVAILABLE <<<

********************************************************************************
[ 59.68] CONTROL EVENT | New barista added (Barista_3). Total baristas: 3
********************************************************************************
```

## Key Metrics to Observe

- **Customer wait times**: How long customers queue
- **Impact of control events**: See queue lengths change after control interventions
- **Barista utilization**: Observe when baristas are idle vs. busy

## Experiment Ideas

### Beginner
1. Change `NUM_BARISTAS = 1` in the script
   - See how wait times increase
2. Change `INITIAL_MEAN_INTERARRIVAL = 2`
   - Simulate busier shop

### Intermediate
3. Modify control panel timing in real-time version
4. Add more control events (e.g., another barista at t=18s)

### Advanced
5. Add queue length visualization
6. Calculate and display barista utilization rates
7. Implement VIP customer priority

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'simpy'`
```bash
pip install simpy
```

**Problem**: Control panel events not visible (standard version)
- This is expected - use the real-time version instead:
```bash
python coffee_shop_simulation_realtime.py
```

**Problem**: Real-time version runs too slow
- Increase `REALTIME_SCALE` in the script (line 33)
- Or decrease `SIM_TIME` (line 31)

## Next Steps

1. Read the full README.md for detailed explanations
2. Study the code comments to understand DES concepts
3. Try the exercises in README.md
4. Modify parameters and observe changes

## File Structure

```
Lab2-Twinning-Coffee-Shop/
├── README.md                              # Full documentation
├── QUICKSTART.md                          # This file
├── requirements.txt                       # Dependencies
├── coffee_shop_simulation.py              # Standard version
└── coffee_shop_simulation_realtime.py     # Real-time version
```

Happy simulating!
