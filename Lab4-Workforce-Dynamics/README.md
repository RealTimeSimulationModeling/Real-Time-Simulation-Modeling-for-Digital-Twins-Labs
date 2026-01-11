# Lab 4: Modeling Workforce Dynamics

## Overview

This lab implements a **System Dynamics (SD)** model of a project-based company's workforce from first principles. Unlike specialized SD software, this implementation uses pure Python with a simple time-step loop (Euler integration) to make the mechanics of stocks, flows, and feedback loops completely transparent.

## Learning Objectives

- Understand System Dynamics fundamentals: stocks, flows, feedback loops
- Recognize the "overshoot" archetype in dynamic systems
- See how aggressive policies can create unintended consequences
- Learn to model non-linear relationships and time delays
- Understand strategic-level Digital Twin applications

## System Dynamics Concepts Demonstrated

### 1. Stocks (State Variables)
**Accumulators that define system state:**
- **Workforce**: Number of employees (people)
- **Project Backlog**: Number of projects waiting (projects)

Stocks change slowly and provide system inertia.

### 2. Flows (Rates of Change)
**Processes that modify stocks:**
- **hiring_rate**: Employees joining per month (inflow to Workforce)
- **quit_rate**: Employees leaving per month (outflow from Workforce)
- **new_projects_rate**: Projects arriving per month (inflow to Backlog)
- **completion_rate**: Projects finished per month (outflow from Backlog)

Flows cause stocks to accumulate or drain.

### 3. Auxiliary Variables
**Computed values that connect stocks and flows:**
- **schedule_pressure**: Projects per person (Backlog/Workforce)
- **productivity_effect**: How pressure affects output
- **quitting_effect**: How pressure affects turnover
- **desired_workforce**: Target staffing level

### 4. Feedback Loops

**Reinforcing Loop R1: Burnout Spiral** (Vicious Cycle)
```
High Pressure → More Quitting → Fewer Workers → Even Higher Pressure → ...
```

**Reinforcing Loop R2: Productivity Collapse**
```
High Pressure → Lower Productivity → More Backlog → Even Higher Pressure → ...
```

**Balancing Loop B1: Hiring Response**
```
More Backlog → Hire More → More Workers → Lower Pressure → ...
```

**The Conflict**: R1 and R2 fight against B1, creating complex dynamics!

### 5. Non-Linear Relationships

**Productivity vs. Pressure** (Yerkes-Dodson Law):
- Low pressure (3 projects/person): 110% productivity (efficient, focused)
- Moderate pressure (5 projects/person): 100% productivity (baseline)
- High pressure (10 projects/person): 60% productivity (overwhelmed)
- Extreme pressure (15+ projects/person): 40% productivity (crisis mode)

**Quitting vs. Pressure** (Exponential):
- Normal pressure (≤5): 1.0x normal turnover
- Pressure = 7: 1.5x turnover
- Pressure = 10: 3.0x turnover (triple!)
- Pressure = 15: 6.0x turnover (exodus)

### 6. The Overshoot Archetype

**Classic SD Pattern**:
1. **Shock**: Big new contract arrives
2. **Aggressive Response**: Rapid hiring to handle load
3. **Initial Success**: Backlog starts decreasing
4. **Overshoot**: Hire too many people too fast
5. **Unintended Consequences**:
   - Schedule pressure remains high during ramp-up
   - Productivity drops (training overhead, confusion)
   - Burnout increases, turnover spikes
   - More hiring needed to replace quitters
6. **Potential Collapse**: System can destabilize

**Key Insight**: The "obvious" solution (hire more!) can make things worse!

## Files in This Lab

### `workforce_dynamics_model.py`
Complete SD model built from scratch

**Components**:
- Simulation constants and initial conditions
- Non-linear effect functions (productivity, quitting)
- Flow calculation functions
- Euler integration loop
- Matplotlib visualization
- Analysis and interpretation
- Digital Twin integration guide

**No Dependencies**: Pure Python + matplotlib (no PySD or specialized SD libraries)

## Installation

### Prerequisites
- Python 3.9 or higher
- matplotlib for visualization

### Setup

```bash
cd Lab4-Workforce-Dynamics
pip install matplotlib
# Or
pip install -r requirements.txt
```

## Running the Simulation

```bash
python workforce_dynamics_model.py
```

### What Happens

1. **Console Output**: Shows simulation progress every 6 months
2. **Month 6**: Shock event announcement (+400 projects)
3. **Analysis**: Printed interpretation of results
4. **Visualization**: Four-panel plot saved and displayed
5. **Digital Twin Guide**: Integration documentation

### Output Files

- `workforce_dynamics_results.png`: Visualization of all key variables

## Understanding the Visualization

### Panel 1: Stock Behavior
**Workforce (blue) and Backlog (orange)**
- Watch for: Workforce overshooting its target
- Notice: Oscillations as system tries to stabilize
- Key moment: When hiring peaks but backlog still high

### Panel 2: Schedule Pressure
**Projects per Person (red)**
- Horizontal line: Nominal pressure (5.0)
- Watch for: Spike after shock event
- Notice: How long it stays elevated
- This drives all the negative effects!

### Panel 3: Workforce Flows
**Hiring (green) vs. Quitting (red)**
- Watch for: Hiring spike after shock
- Notice: Delayed quit rate spike (burnout takes time)
- Key insight: When quitting exceeds hiring (crisis!)

### Panel 4: Productivity Effect
**Multiplier on baseline productivity**
- 1.0 = normal productivity
- <1.0 = degraded performance
- Watch for: How pressure crushes productivity
- Notice: This amplifies the backlog problem

## Simulation Scenario

### Timeline

**Month 0-5**: Equilibrium
- 100 employees, 500 project backlog
- Steady state: 20 new projects/month, completing 20/month
- Schedule pressure: 5 projects/person
- Everything stable

**Month 6**: SHOCK EVENT
- Big contract arrives: +400 projects
- Backlog jumps from 500 → 900
- Pressure spikes from 5 → 9 projects/person
- Company responds with aggressive hiring

**Month 7-18**: Overshoot Phase
- Rapid hiring to handle increased workload
- Workforce grows quickly (might reach 140-160)
- But: High pressure degrades productivity
- And: Burnout starts building
- Result: Progress slower than expected

**Month 19-30**: Consequence Phase
- Accumulated burnout manifests as high turnover
- Quit rate spikes (might hit 6-8 people/month)
- Must hire just to replace quitters
- Productivity remains low (training new people)
- Backlog may start growing again!

**Month 31-36**: Stabilization Attempt
- System tries to find new equilibrium
- May oscillate before settling
- Final state might be worse than initial!

## Key Parameters

### Simulation Configuration
```python
SIMULATION_MONTHS = 36       # 3 years
DT = 1.0                     # 1-month time step
TIME_SHOCK = 6               # When shock occurs
```

### Initial State
```python
INITIAL_WORKFORCE = 100      # Employees
INITIAL_BACKLOG = 500        # Projects
```

### Productivity
```python
NOMINAL_PRODUCTIVITY = 5.0   # Projects/person/month
NOMINAL_SCHEDULE_PRESSURE = 5.0  # Baseline pressure
```

### Workforce Dynamics
```python
NORMAL_QUIT_RATE_FRACTION = 0.05  # 5% annual turnover
TIME_TO_ADJUST_HIRING = 3.0       # Months to close hiring gap
PROJECTS_PER_DESIRED_EMPLOYEE = 5.0  # Staffing ratio
```

### External Input
```python
NEW_PROJECTS_RATE = 20.0     # New projects/month
SHOCK_SIZE = 400             # Extra projects from contract
```

## Exercises and Extensions

### Beginner

1. **Different Shock Sizes**
   - Change `SHOCK_SIZE` to 200 or 600
   - How does the system respond differently?

2. **Slower Hiring**
   - Change `TIME_TO_ADJUST_HIRING` to 6 months
   - Does this prevent overshoot?

3. **Different Baseline**
   - Change `INITIAL_WORKFORCE` to 150
   - Does a larger company handle shocks better?

### Intermediate

4. **Modified Productivity Curve**
   - Make productivity less sensitive to pressure
   - Edit `calculate_effect_of_pressure_on_productivity()`
   - How does this change outcomes?

5. **Add Experience Effect**
   - Track average employee tenure
   - Experienced teams are more productive
   - New hires drag down average

6. **Multiple Shocks**
   - Add a second shock at month 20
   - How does the system respond when already stressed?

### Advanced

7. **Adaptive Hiring Policy**
   - Make hiring responsive to quit rate
   - Don't just look at backlog, also consider turnover
   - Can you prevent overshoot?

8. **Training Delay**
   - New hires aren't immediately productive
   - Add a "Training" stock between hiring and full productivity
   - This exacerbates the overshoot!

9. **Optimize Policy**
   - Use scipy.optimize to find best hiring trajectory
   - Minimize: Total time above pressure threshold
   - Subject to: Budget constraints

10. **Full Causal Loop Diagram**
    - Draw the complete stock-flow diagram
    - Identify all feedback loops
    - Calculate loop dominance over time

## System Dynamics vs Other Modeling Approaches

### Comparison with Previous Labs

| Aspect | DES (Lab 2) | ABM (Lab 3) | SD (Lab 4) |
|--------|-------------|-------------|------------|
| **Focus** | Process flow | Individual agents | Aggregate behavior |
| **Time Scale** | Minutes/hours | Seconds/minutes | Months/years |
| **Entities** | Discrete (customers) | Discrete (AGVs) | Continuous (employees) |
| **Purpose** | Operational | Tactical | Strategic |
| **Key Feature** | Queues | Emergence | Feedback loops |

### When to Use SD

**Good For:**
- Strategic planning (months/years horizon)
- Policy analysis and testing
- Understanding feedback dynamics
- Non-linear relationships
- Aggregate population flows
- Counter-intuitive system behavior

**Not Good For:**
- Detailed process optimization (use DES)
- Individual entity tracking (use ABM)
- Short-term scheduling (use optimization)
- Static equilibrium analysis (use spreadsheets)

## The Euler Integration Method

### What Is It?

System Dynamics models are systems of differential equations. To simulate them, we need numerical integration. **Euler's method** is the simplest:

```
New_Value = Old_Value + (Rate_of_Change) * Time_Step
```

### In Our Model

```python
# Workforce stock update
workforce += (hiring_rate - quit_rate) * DT

# Backlog stock update
project_backlog += (NEW_PROJECTS_RATE - completion_rate) * DT
```

### Why Euler?

**Pros:**
- Extremely simple to understand
- Transparent (can see exactly what's happening)
- Good enough for educational purposes
- Fast computation

**Cons:**
- Can be inaccurate with large time steps
- Can become unstable with stiff equations
- Professional SD software uses Runge-Kutta (more accurate)

**For This Lab**: Euler is perfect because our time step (1 month) is small relative to system dynamics, and we value transparency over precision.

## Digital Twin Applications

### Strategic Workforce Planning Twin

This model represents a **strategic-level** Digital Twin:

**Characteristics:**
- Monthly/quarterly update frequency
- Focuses on aggregate trends, not individuals
- Supports executive decision-making
- Long-term forecasting (6-12 months)

**Use Cases:**

1. **Predictive Planning**
   - "Given current backlog, how many people should we hire?"
   - "When will the backlog return to normal levels?"

2. **Policy Testing**
   - "Should we hire 20 people immediately or 5/month for 4 months?"
   - "What happens if we freeze hiring?"

3. **Risk Assessment**
   - "What's the probability of schedule pressure exceeding 8?"
   - "Could we experience a burnout crisis?"

4. **Scenario Analysis**
   - "What if we win this big contract?"
   - "What if 10% of the team quits (acquisition by competitor)?"

### Data Integration

**Required Real-World Data** (Monthly):
- Total headcount (from HRIS)
- Active project count (from PMO)
- New hires (from recruiting system)
- Voluntary departures (from HR)
- Projects completed (from project management tool)

**Model Calibration Data** (Historical):
- 2-3 years of monthly data
- Used to fit productivity and quit rate functions
- Validated by comparing simulation to history

### Integration Architecture

See the detailed guide in the script's `DIGITAL_TWIN_INTEGRATION_GUIDE` section for:
- Data source mapping
- API integration examples
- Calibration workflow
- Operational modes
- Success metrics

## Interpreting Results

### What You Should See

Running the default configuration, you should observe:

1. **Initial Stability** (Months 0-5)
   - Flat workforce and backlog
   - Low pressure
   - Everything balanced

2. **Shock Impact** (Month 6)
   - Backlog jumps dramatically
   - Pressure spikes immediately
   - Hiring response begins

3. **Aggressive Hiring** (Months 7-15)
   - Workforce grows rapidly
   - Hiring rate peaks around 10-15/month
   - Backlog starts declining

4. **The Overshoot** (Months 10-20)
   - Workforce exceeds sustainable level
   - Pressure remains high (training, coordination overhead)
   - Productivity degraded
   - Burnout accumulating

5. **The Crash** (Months 20-30)
   - Quit rate spikes to 6-8/month
   - Must hire just to replace departures
   - Backlog may grow again
   - Morale crisis

6. **Attempted Stabilization** (Months 30-36)
   - System oscillates seeking equilibrium
   - May end up worse than initial state
   - Lesson: Aggressive response backfired!

### Key Insight

**The Problem**: Hiring addresses the symptom (backlog) but ignores the root cause (sustainable workload and morale).

**Better Approaches** (Test these!):
- Gradual hiring over longer period
- Reduce incoming projects (negotiate deadlines)
- Improve productivity through process improvements
- Combination of modest hiring + scope reduction

## Troubleshooting

### Simulation Doesn't Run
```bash
pip install matplotlib numpy
```

### Unexpected Results

**Workforce Goes Negative**:
- Check: `workforce = max(1, workforce)` line exists
- This prevents company from disappearing

**Backlog Grows Forever**:
- Check: Is productivity too low?
- Check: Is quit rate too high?
- May need to adjust effect functions

**No Overshoot Visible**:
- Try larger `SHOCK_SIZE` (600 or 800)
- Try faster hiring (`TIME_TO_ADJUST_HIRING = 2`)

### Plot Doesn't Display

**On a server without display**:
```python
# Add at top of main()
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
```

Then check `workforce_dynamics_results.png` file.

## Mathematical Formulation

For those interested in the formal SD notation:

### Stock Equations
```
dWorkforce/dt = hiring_rate - quit_rate
dBacklog/dt = new_projects_rate - completion_rate
```

### Flow Equations
```
hiring_rate = (desired_workforce - Workforce) / TIME_TO_ADJUST_HIRING
quit_rate = Workforce * (NORMAL_QUIT_RATE / 12) * quitting_effect
completion_rate = Workforce * NOMINAL_PRODUCTIVITY * productivity_effect
```

### Auxiliary Equations
```
schedule_pressure = Backlog / Workforce
desired_workforce = Backlog / PROJECTS_PER_DESIRED_EMPLOYEE
productivity_effect = f(schedule_pressure)  # Non-linear function
quitting_effect = g(schedule_pressure)       # Non-linear function
```

This is a 2nd-order system (2 stocks) with non-linear auxiliary functions.

## References

### System Dynamics

- **Sterman, J.D.** "Business Dynamics: Systems Thinking and Modeling for a Complex World" (2000)
  - The definitive SD textbook
  - Chapters 5-8 cover stocks, flows, feedback

- **Forrester, J.W.** "Industrial Dynamics" (1961)
  - Original SD work
  - Manufacturing supply chain model

- **Meadows, D.H.** "Thinking in Systems: A Primer" (2008)
  - Accessible introduction
  - Great for understanding archetypes

### Workforce Dynamics

- **Abdel-Hamid, T.K.** "The Dynamics of Software Project Staffing" (1989)
  - Classic SD model of software projects
  - This lab is inspired by Abdel-Hamid's work

- **Brooks, F.** "The Mythical Man-Month" (1975)
  - "Adding manpower to a late project makes it later"
  - Complements SD understanding of staffing dynamics

## Author Notes

This lab demonstrates:
- System Dynamics fundamentals
- Building SD models from scratch
- Feedback loop analysis
- Overshoot archetype
- Strategic Digital Twin applications

The code prioritizes **transparency** over sophistication. Every calculation is explicit. The goal is to demystify SD and make the mechanics visible.

The "overshoot" result isn't guaranteed - it depends on parameter values. Real companies show this pattern, but your specific numbers matter. Calibration is key!

## Next Steps

After completing this lab:
1. Experiment with different parameter values
2. Try the exercises (start with shock size variations)
3. Draw the causal loop diagram by hand
4. Compare SD approach to Labs 2 and 3
5. Think about combining approaches (hybrid models!)
6. Consider real-world applications in your domain

Happy modeling! May your feedback loops be well-balanced!
