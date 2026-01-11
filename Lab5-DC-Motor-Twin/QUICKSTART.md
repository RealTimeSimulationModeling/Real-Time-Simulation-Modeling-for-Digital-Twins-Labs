# Quick Start Guide - Lab 5: DC Motor Digital Twin

## 60-Second Setup

```bash
# 1. Navigate to the lab directory
cd Lab5-DC-Motor-Twin

# 2. Install dependencies
pip install numpy scipy matplotlib

# 3. Run the simulation
python dc_motor_twin.py
```

## What You'll See

### Console Output

The script walks through the complete Digital Twin workflow:

**Step 1: Data Generation**
```
Generating synthetic 'real' motor data...
  Generated 1000 data points over 10 seconds
  Peak velocity: 84.32 rad/s
  Peak current: 5.67 A
```

**Step 2: Initial Model (Before Calibration)**
```
Initial RMSE: 8.4521 rad/s
→ Model doesn't match data well yet. Calibration needed!
```

**Step 3: Calibration**
```
Calibrated RMSE: 1.2341 rad/s
Improvement: 85.4% reduction in error
→ Model now accurately represents the real motor!
```

**Step 4-5: Validation & Virtual Sensor**
```
Temperature Profile:
  Initial: 25.0°C (ambient)
  Peak: 78.3°C
  Final: 72.1°C
  Temperature rise: 47.1°C

✓ Motor temperature within safe range
```

### Visualization Outputs

**File 1: `dc_motor_validation.png`** (3 panels)
1. **Input Voltage**: Step function (0V → 12V at t=2s)
2. **Angular Velocity**: Model vs. Measured (key validation!)
3. **Current**: Additional validation metric

**File 2: `dc_motor_virtual_sensor.png`** (2 panels)
1. **Armature Current**: Direct measurement
2. **Temperature**: Virtual sensor (estimated, not measured!)

## Understanding the Physics

### The DC Motor in 3 Equations

**1. Electrical (Fast - milliseconds)**
```
di/dt = (V - R·i - L_e·ω) / L
```
- Voltage V pushes current through resistance R and inductance L
- Back-EMF (L_e·ω) opposes current as motor spins
- Current response is fast due to small inductance

**2. Mechanical (Medium - tens of milliseconds)**
```
dω/dt = (K_t·i - b·ω) / J
```
- Current i generates electromagnetic torque (K_t·i)
- Friction opposes motion (b·ω)
- Inertia J resists acceleration

**3. Thermal (Slow - seconds)**
```
dT/dt = (R·i² - (T - T_amb)/R_th) / C_th
```
- I²R losses heat the motor
- Heat flows to environment through thermal resistance
- Thermal mass slows temperature changes

### The Input: Step Voltage

```
Time:     0s -------- 2s -------- 10s
Voltage:  0V         12V        12V
          [Motor off] [Motor accelerates and stabilizes]
```

This simple input reveals rich dynamics:
- Initial acceleration (overcoming inertia)
- Current spike at startup (low back-EMF)
- Steady-state operation (balanced torques)
- Temperature rise (continuous heat generation)

## What to Look For

### Validation Plot (Critical!)

**Panel 2: Angular Velocity**

**Before Calibration** (dotted line strays from real data):
- Model peaks at wrong speed
- Wrong acceleration rate
- Doesn't match steady-state

**After Calibration** (solid line hugs real data):
- ✅ Matches transient response
- ✅ Correct steady-state speed
- ✅ RMSE reduced by 85%+

**RMSE Box**: Shows quantitative fit quality
- <2 rad/s = Excellent
- 2-5 rad/s = Good
- >5 rad/s = Needs more calibration

### Virtual Sensor Plot (Key Innovation!)

**Panel 2: Temperature**

**What's Special**:
- This is NOT measured directly!
- Estimated from physics + current measurement
- Impossible to get without embedded thermocouples

**Typical Profile**:
```
0-2s:   T = 25°C (motor off, ambient)
2-4s:   T rises rapidly (high startup current)
4-10s:  T continues rising but slower (approaching equilibrium)
Final:  T ~ 70-80°C (thermal steady-state)
```

**Warning Indicators**:
- Red dashed line: Safety threshold (80°C)
- Red shaded area: Danger zone
- Yellow annotation: Final temperature with rise amount

### What Makes It a "Digital Twin"?

**Characteristic 1: Physics-Based**
- Not just curve fitting
- Based on fundamental laws (Kirchhoff, Newton, Fourier)
- Parameters have physical meaning (R in Ohms, J in kg·m²)

**Characteristic 2: Validated**
- Model matches real motor behavior (RMSE metric)
- Calibrated parameters close to true values
- Can predict response to new inputs

**Characteristic 3: Virtual Sensing**
- Estimates unmeasurable quantities (temperature)
- Uses measurable inputs (voltage, current)
- Enables new capabilities (thermal monitoring)

**Characteristic 4: Predictive**
- Can forecast future states
- Run "what-if" scenarios
- Optimize before implementation

## Quick Experiments

### Experiment 1: Change Voltage Level
```python
# In generate_real_data(), change:
return 24.0 if t >= 2.0 else 0.0  # Instead of 12.0
```
**Question**: How does temperature change? Why does speed increase?

### Experiment 2: Longer Runtime
```python
# Change time span:
t_span = (0, 30)  # Instead of (0, 10)
t_eval = np.linspace(0, 30, 3000)
```
**Question**: Does temperature reach thermal equilibrium? At what value?

### Experiment 3: Different Input Pattern
```python
# Try PWM (pulse width modulation):
def voltage_input(t):
    return 12.0 if (t % 0.1) < 0.05 else 0.0  # 50% duty cycle, 10Hz
```
**Question**: How does average speed compare to DC voltage?

### Experiment 4: Parameter Sensitivity
```python
# In params_calibrated, change one parameter:
J=0.020,  # Double the inertia
```
**Question**: How does acceleration change? Why?

## The Three-Part Story

### Part 1: Build the Model (Lines 1-200)

**What's Happening**:
- Defining physical parameters (R, L, J, etc.)
- Implementing the 3 ODEs (electrical, mechanical, thermal)
- Using scipy.integrate.solve_ivp to solve numerically

**Key Insight**: The model is just physics equations translated to Python!

### Part 2: Calibrate & Validate (Lines 201-400)

**What's Happening**:
- Generate "real" data with true parameters
- Try model with initial guess (doesn't match)
- Adjust parameters until good fit (calibration)
- Quantify fit quality with RMSE

**Key Insight**: Real motors have unknown parameters - calibration finds them!

### Part 3: Virtual Sensor (Lines 401-end)

**What's Happening**:
- Validated model used to estimate temperature
- Temperature calculated from physical laws
- No temperature sensor needed!

**Key Insight**: Physics models enable virtual sensing - measure the unmeasurable!

## Common Patterns You'll See

### Pattern 1: Startup Transient
```
t = 0-2s:   Everything zero (motor off)
t = 2.0s:   Voltage step applied
t = 2.0-2.5s: Current spikes (low back-EMF)
t = 2.5-4s: Speed ramps up (electromagnetic torque)
t = 4-10s:  Steady-state (torque = friction)
```

### Pattern 2: Current Spike
**Why it happens**:
- At startup, ω = 0 → back-EMF = 0
- Full voltage appears across R+L
- Current jumps to V/R
- As ω increases, back-EMF rises, current drops

**Physical analogy**: Like pushing a heavy box - hardest at start!

### Pattern 3: Temperature Rise
**Why it never plateaus at 10s**:
- Thermal time constant is longer than mechanical
- Takes 20-30 seconds to reach thermal equilibrium
- I²R losses are continuous
- Heat dissipation is slow

**If you ran longer**: T would level off around 80-90°C

## Key Metrics Explained

### RMSE (Root Mean Square Error)
```
RMSE = √(mean((simulated - measured)²))
```

**Interpretation**:
- Units same as measurement (rad/s for velocity)
- Represents "typical" error magnitude
- Lower is better
- <2% of signal range = excellent

**Example**:
- Speed range: 0 to 100 rad/s
- RMSE = 1.5 rad/s
- Relative error: 1.5%
- **Grade: Excellent!**

### Temperature Rise
```
ΔT = T_final - T_ambient
```

**Typical Values**:
- Small motors: 20-40°C rise
- Medium motors: 40-60°C rise
- Large motors: 60-80°C rise

**Safety Limits**:
- Class A insulation: 105°C max
- Class B insulation: 130°C max
- Class F insulation: 155°C max

## Troubleshooting

**Problem**: Plots don't appear
```bash
# Check matplotlib backend:
python -c "import matplotlib; print(matplotlib.get_backend())"

# If 'agg', plots saved but not shown
# Files are still created: dc_motor_*.png
```

**Problem**: "Integration failed"
```
# Usually means parameters are unrealistic
# Check for:
- Negative values (R, L, J must be > 0)
- Very small values (J < 1e-6 can cause issues)
- Very large values (R > 100 unusual for small motor)
```

**Problem**: Model doesn't fit data
```
# This is expected with initial guess!
# After calibration, RMSE should drop significantly
# If not, check parameter values are reasonable
```

**Problem**: Temperature goes to infinity
```
# Check thermal parameters:
- R_th must be > 0
- C_th must be > 0
- Make sure you're using calibrated params, not initial guess
```

## What Makes This Different?

### vs. Lab 2 (DES - Coffee Shop)
- **Lab 2**: Discrete events, queuing
- **Lab 5**: Continuous time, differential equations
- **Lab 2**: Statistical, aggregate
- **Lab 5**: Physics-based, deterministic

### vs. Lab 3 (ABM - Warehouse AGVs)
- **Lab 3**: Individual agents, emergence
- **Lab 5**: Single system, coupled dynamics
- **Lab 3**: Spatial, rule-based
- **Lab 5**: Temporal, equation-based

### vs. Lab 4 (SD - Workforce)
- **Lab 4**: Aggregate flows, feedback loops
- **Lab 5**: Detailed states, multi-domain coupling
- **Lab 4**: Monthly timescale, strategic
- **Lab 5**: Millisecond timescale, control

**When to use Lab 5 approach**:
- Detailed physical system
- Real-time control
- Virtual sensing needed
- High accuracy required

## The Bottom Line

**This lab shows**: A physics-based Digital Twin can:
1. **Model** a DC motor from first principles (3 coupled ODEs)
2. **Calibrate** to match real motor data (parameter identification)
3. **Predict** motor behavior under different conditions
4. **Estimate** unmeasurable quantities (virtual temperature sensor)

**Why it matters**:
- No expensive temperature sensors needed
- Predict overheating before damage
- Optimize control for efficiency
- Design better motors virtually

**Key technique**: scipy.integrate.solve_ivp
- Industry-standard ODE solver
- Handles stiff equations
- Adaptive step size
- Multiple integration methods

---

**Now run it and watch physics come alive! ⚡🔬**
