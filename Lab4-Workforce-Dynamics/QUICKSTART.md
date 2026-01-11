# Quick Start Guide - Lab 4: Workforce Dynamics

## 60-Second Setup

```bash
# 1. Navigate to the lab directory
cd Lab4-Workforce-Dynamics

# 2. Install dependencies
pip install matplotlib numpy

# 3. Run the simulation
python workforce_dynamics_model.py
```

## What You'll See

### Console Output

1. **Simulation Header**
   - Configuration summary
   - Initial conditions

2. **Progress Updates** (every 6 months)
   ```
   Month  0: Workforce= 100.0, Backlog= 500.0, Pressure=5.00, ...
   Month  6: Workforce= 108.5, Backlog= 900.0, Pressure=8.30, ...
   ```

3. **Shock Event Announcement**
   ```
   ======================================================================
   MONTH 6: BIG CONTRACT SHOCK!
     +400 projects added to backlog
     New backlog: 900 projects
   ======================================================================
   ```

4. **Analysis Report**
   - Peak values identified
   - System response described
   - Key insights highlighted

5. **Digital Twin Integration Guide**
   - Data source mapping
   - API integration examples
   - Calibration workflow

### Visualization

A 4-panel plot showing:
1. **Workforce & Backlog** - Stock behavior over time
2. **Schedule Pressure** - The key driver of system dynamics
3. **Hiring vs Quitting** - Flow dynamics
4. **Productivity Effect** - Non-linear impact of pressure

Saved as: `workforce_dynamics_results.png`

## What to Look For

### The Overshoot Story

**Act 1: Equilibrium** (Months 0-5)
- Flat lines = stable system
- 100 employees handling 500 projects
- 5 projects/person (comfortable workload)

**Act 2: Shock** (Month 6)
- Vertical jump in backlog (500 → 900)
- Pressure spikes immediately
- Aggressive hiring response begins

**Act 3: The "Fix"** (Months 7-18)
- Workforce grows rapidly (reaches 140-160)
- Hiring rate peaks (10-15 people/month)
- Backlog starts declining
- **Looks successful... but wait!**

**Act 4: Unintended Consequences** (Months 19-30)
- Productivity drops (too much pressure, training overhead)
- **Quit rate SPIKES** (6-8 people/month!)
- Burnout spiral kicks in
- Must hire just to replace quitters
- Backlog may grow again!

**Act 5: The Aftermath** (Months 30-36)
- System oscillates trying to stabilize
- May end up worse than initial state
- **Lesson**: Aggressive response backfired!

### Key Metrics to Watch

**Workforce (Panel 1, Blue Line)**
- Look for: Overshoot above sustainable level
- Peak around month 15-18
- Should eventually return to ~100, but watch the path!

**Schedule Pressure (Panel 2, Red Line)**
- Horizontal green line = nominal (5.0)
- Spike after shock (goes to 8-9)
- **Critical**: How long does it stay elevated?
- High pressure = everything breaks down

**Quit Rate (Panel 3, Red Line)**
- Normal: ~0.4 people/month
- After shock: Can hit 6-8 people/month!
- **This is the burnout crisis**
- Notice the delay (takes ~12 months to manifest)

**Productivity (Panel 4, Purple Line)**
- Nominal = 1.0 (100% efficiency)
- Drops to 0.6-0.7 when pressure is high
- **This amplifies the problem**
- Can't complete projects when everyone is overwhelmed

## Understanding the Feedback Loops

### Reinforcing Loop R1: Burnout Spiral (BAD!)
```
More Pressure → More People Quit → Fewer Workers → Even More Pressure
```
**Why it matters**: This can spiral out of control!

### Reinforcing Loop R2: Productivity Collapse (BAD!)
```
More Pressure → Lower Productivity → More Backlog → Even More Pressure
```
**Why it matters**: Makes the backlog problem worse!

### Balancing Loop B1: Hiring Response (GOOD!)
```
More Backlog → Hire More People → More Workers → Lower Pressure
```
**Why it matters**: This is management's intended fix

**The Battle**: R1 and R2 fight against B1!
- If R1/R2 win: System collapses
- If B1 wins: System stabilizes
- Often: They oscillate for a while

## Quick Experiments

### Experiment 1: Gentler Shock
```python
# In workforce_dynamics_model.py, change:
SHOCK_SIZE = 200  # Instead of 400
```
**Question**: Does a smaller shock prevent overshoot?

### Experiment 2: Slower Hiring
```python
# Change:
TIME_TO_ADJUST_HIRING = 6.0  # Instead of 3.0
```
**Question**: Does gradual hiring prevent burnout?

### Experiment 3: Better Productivity
```python
# In calculate_effect_of_pressure_on_productivity()
# Change the decline rates to be less severe
# Example: return 0.9 instead of 0.6 for high pressure
```
**Question**: If teams are more resilient, does overshoot disappear?

### Experiment 4: Multiple Shocks
```python
# In run_simulation(), add:
if t == 20:
    project_backlog += 300
    print("SECOND SHOCK!")
```
**Question**: Can an already-stressed system handle another blow?

## Common Patterns You Might See

### Pattern 1: Clean Overshoot
- Workforce peaks around month 15
- Quit rate spikes around month 22
- Eventually stabilizes but oscillates
- **Interpretation**: Classic overshoot archetype

### Pattern 2: Collapse
- Workforce drops below initial level
- Backlog grows out of control
- Pressure exceeds 15
- **Interpretation**: Burnout spiral won (R1 dominated)
- **Fix needed**: Reduce shock size or slow hiring

### Pattern 3: Quick Recovery
- Minimal overshoot
- Backlog returns to normal by month 24
- Low oscillation
- **Interpretation**: Parameters are more conservative
- **Either**: Shock too small OR hiring too slow

## Troubleshooting

**Problem**: No plot appears
```bash
# Check that matplotlib is installed:
pip install matplotlib

# If on a server, the plot is still saved:
ls -la workforce_dynamics_results.png
```

**Problem**: Weird results (workforce goes to 1000+)
- Check your parameter modifications
- Did you accidentally change DT or multiply instead of divide?
- Restore default parameters and try again

**Problem**: Simulation crashes
```
# Check Python version:
python --version  # Should be 3.9+

# Reinstall dependencies:
pip install --upgrade matplotlib numpy
```

## What Makes This "System Dynamics"?

### SD Signature Features You'll See:

1. **Stocks** (Things that accumulate)
   - Workforce, Backlog
   - Change slowly, provide inertia

2. **Flows** (Rates of change)
   - Hiring, Quitting, Completions
   - Cause stocks to grow or shrink

3. **Feedback Loops** (Circular causality)
   - Not linear cause-effect!
   - System influences itself

4. **Time Delays** (Things take time)
   - Hiring takes 3 months to adjust
   - Burnout builds gradually
   - Delays cause overshoot!

5. **Non-Linearity** (Relationships aren't straight lines)
   - Pressure effect on productivity
   - Pressure effect on quitting
   - This creates surprises!

6. **Counter-Intuitive Behavior**
   - "Obvious" solution makes things worse
   - Aggressive response creates problems
   - This is why SD matters!

## Key Takeaways

### Technical Lessons
✓ Built SD model from scratch (no special libraries)
✓ Used Euler integration (simple time-stepping)
✓ Implemented stocks, flows, auxiliaries
✓ Created non-linear effect functions
✓ Visualized system behavior

### Conceptual Lessons
✓ Feedback loops create complex behavior
✓ Time delays cause overshoot
✓ Aggressive policies can backfire
✓ Need to think in terms of system structure, not events
✓ Strategic planning requires understanding dynamics

### Digital Twin Lessons
✓ SD good for strategic-level twins (months/years)
✓ Different from operational twins (Labs 2-3)
✓ Requires aggregate data, not detailed transactions
✓ Used for policy testing, not real-time control
✓ Complements other modeling approaches

## Next Steps

1. **Read the full README.md** for deep dive
2. **Try the experiments** above
3. **Modify parameters** and observe changes
4. **Draw the feedback loops** by hand
5. **Think about applications** in your domain

## File Structure

```
Lab4-Workforce-Dynamics/
├── README.md                         # Full documentation
├── QUICKSTART.md                     # This file
├── requirements.txt                  # Dependencies
├── workforce_dynamics_model.py       # Main simulation
└── workforce_dynamics_results.png    # Generated plot
```

## The Bottom Line

**This lab shows**: Aggressive hiring to handle a workload spike can create a burnout crisis that makes things worse.

**Why**: High pressure degrades productivity and increases turnover, creating reinforcing spirals that overwhelm the intended balancing loop.

**Solution**: More gradual, sustainable responses that account for feedback dynamics.

**SD Value**: Reveals these non-obvious consequences BEFORE implementing the policy in real life!

---

**Now run it and watch the overshoot unfold! 📈📉**
