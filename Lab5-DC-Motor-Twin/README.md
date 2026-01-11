# Lab 5: Twinning a DC Motor

## Overview

This lab implements a **physics-based Digital Twin** of a DC motor using ordinary differential equations (ODEs). Unlike the previous labs which focused on discrete events, agents, or aggregate flows, this lab demonstrates **continuous-time modeling** based on first-principles physics. It showcases the complete Digital Twin development workflow: modeling, calibration, validation, and virtual sensing.

## Learning Objectives

- Understand physics-based modeling using ODEs
- Implement coupled multi-domain systems (electrical-mechanical-thermal)
- Learn numerical ODE solving with scipy
- Practice model calibration and parameter identification
- Create virtual sensors for unmeasurable quantities
- Validate models against real data

## Physics-Based Modeling Concepts

### Why Physics-Based Models?

**Advantages**:
- Based on fundamental laws (universal truth)
- Extrapolate beyond training data
- Interpretable parameters with physical meaning
- Can predict unmeasurable quantities
- Require less data than pure machine learning

**When to Use**:
- System physics is well understood
- High accuracy needed
- Extrapolation beyond observed conditions
- Virtual sensing requirements
- Safety-critical applications

### The DC Motor System

A DC motor converts electrical energy to mechanical motion through electromagnetic forces. It involves three coupled physical domains:

**1. Electrical Domain** (Armature Circuit)
```
V(t) = R·i + L·(di/dt) + L_e·ω
```
- V: Applied voltage (control input)
- i: Armature current (electrical state)
- ω: Angular velocity (creates back-EMF)

**2. Mechanical Domain** (Rotor Dynamics)
```
J·(dω/dt) = K_t·i - b·ω
```
- K_t·i: Electromagnetic torque (coupling from electrical)
- b·ω: Friction torque (opposes motion)
- J: Rotor inertia (resistance to acceleration)

**3. Thermal Domain** (Heat Generation and Dissipation)
```
C_th·(dT/dt) = R·i² - (T - T_ambient)/R_th
```
- R·i²: Joule heating (I²R losses)
- (T - T_ambient)/R_th: Cooling to environment
- C_th: Thermal mass

### State-Space Representation

The complete system is described by **3 coupled first-order ODEs**:

```python
State vector: y = [ω, i, T]

dy/dt = f(t, y, u)

where:
  dω/dt = (K_t·i - b·ω) / J
  di/dt = (V - R·i - L_e·ω) / L
  dT/dt = (R·i² - (T - T_ambient)/R_th) / C_th
```

**Key Features**:
- **Coupling**: Current i appears in both electrical and mechanical equations
- **Non-linearity**: i² term in thermal equation
- **Time scales**: Electrical (ms), Mechanical (10s of ms), Thermal (seconds)

## Files in This Lab

### `dc_motor_twin.py`
Complete physics-based Digital Twin implementation

**Components**:
- DCMotorParameters dataclass (physical constants)
- dc_motor_model() function (ODE system)
- generate_real_data() (synthetic measurements)
- simulate_motor() (ODE solver wrapper)
- Calibration helpers
- Visualization functions
- Complete workflow demonstration

## Installation

### Prerequisites
- Python 3.9 or higher
- Scientific computing libraries

### Setup

```bash
cd Lab5-DC-Motor-Twin
pip install -r requirements.txt
# Or install directly:
pip install numpy scipy matplotlib
```

## Running the Simulation

```bash
python dc_motor_twin.py
```

### What Happens

1. **Data Generation**: Creates synthetic "real" motor measurements
2. **Initial Evaluation**: Tests model with guessed parameters (poor fit)
3. **Calibration**: Uses improved parameters (good fit)
4. **Validation Plots**: Compares simulation vs. measurements
5. **Virtual Sensor**: Estimates internal temperature
6. **Summary**: Reports error metrics and capabilities

### Output Files

- `dc_motor_validation.png`: Model validation plots
- `dc_motor_virtual_sensor.png`: Temperature estimation plots

## Understanding the Simulation

### The Physics

**Electrical Circuit**:
```
    +---[R]---[L]---+
    |               |
  V(t)          ω → (back-EMF)
    |               |
    +---------------+
```

- Applied voltage V drives current through resistance R and inductance L
- Spinning motor generates back-EMF (L_e·ω) that opposes current
- Faster spin → higher back-EMF → lower current → torque limit

**Mechanical System**:
```
  Torque_motor = K_t · i
  Torque_friction = b · ω

  Net Torque = J · (dω/dt)
```

- Current generates electromagnetic torque
- Friction opposes motion (proportional to speed)
- Inertia resists acceleration

**Thermal System**:
```
  Heat IN: R · i² (I²R losses in windings)
  Heat OUT: (T - T_ambient) / R_th (cooling)

  Temperature rise stored in thermal mass C_th
```

### The Three-Part Workflow

#### Part 1: Build the Model

**Implement ODEs from first principles:**

```python
def dc_motor_model(t, y, voltage_func, params):
    omega, i, temp = y
    V = voltage_func(t)

    # Electrical dynamics (Kirchhoff's Law)
    di_dt = (V - params.R*i - params.L_e*omega) / params.L

    # Mechanical dynamics (Newton's 2nd Law)
    domega_dt = (params.K_t*i - params.b*omega) / params.J

    # Thermal dynamics (Heat transfer)
    P_heat = params.R * i**2
    Q_cool = (temp - params.T_ambient) / params.R_th
    dtemp_dt = (P_heat - Q_cool) / params.C_th

    return [domega_dt, di_dt, dtemp_dt]
```

**Why scipy.integrate.solve_ivp?**
- Industry-standard ODE solver
- Adaptive step size (accuracy + efficiency)
- Multiple integration methods (RK45, Radau, etc.)
- Error control through tolerances

#### Part 2: Calibrate & Validate

**The Challenge**: Real motors have unknown parameters

**The Process**:
1. Collect measurements (voltage in, velocity out)
2. Run simulation with initial parameter guesses
3. Compare simulation to measurements (calculate RMSE)
4. Adjust parameters to minimize error
5. Repeat until satisfactory fit

**In This Lab**:
- "Real" data generated with params_true
- Initial guess uses params_initial_guess (different values)
- Calibrated parameters close to params_true
- RMSE metric quantifies fit quality

**Validation Metrics**:
```
RMSE = √(mean((predicted - measured)²))

Good fit: RMSE < 5% of signal range
Excellent fit: RMSE < 2% of signal range
```

#### Part 3: Virtual Sensor

**The Problem**: Internal motor temperature is hard to measure
- Requires embedded thermocouples
- Adds cost and complexity
- Can't retrofit existing motors

**The Solution**: Estimate it using physics!
- Measure voltage and current (easy)
- Physics model calculates heat generation (R·i²)
- Thermal dynamics predict temperature evolution
- **Virtual sensor**: Temperature estimated without direct measurement

**Value Proposition**:
- Predict overheating before damage
- Optimize cooling systems
- Enable thermal-aware control
- No hardware modifications needed

## Physical Parameters Explained

### Electrical Parameters

**R - Armature Resistance** (Ohms)
- Measured with: Ohmmeter (motor stationary)
- Typical values: 0.5 - 5 Ω for small motors
- Effect: Higher R → more heat, slower acceleration

**L - Armature Inductance** (Henries)
- Measured with: LCR meter
- Typical values: 0.1 - 1 mH for small motors
- Effect: Higher L → slower current response

**L_e - Back-EMF Constant** (V·s/rad)
- Measured from: No-load speed test
- Relationship: V_no_load = L_e · ω_no_load
- Effect: Determines speed-torque characteristics

### Mechanical Parameters

**J - Moment of Inertia** (kg·m²)
- Measured with: Torsion pendulum or acceleration test
- Typical values: 10⁻⁵ - 10⁻³ kg·m² for small motors
- Effect: Higher J → slower acceleration

**b - Viscous Friction** (N·m·s/rad)
- Measured from: Coast-down test
- Effect: Higher b → lower top speed

**K_t - Torque Constant** (N·m/A)
- Measured with: Torque-current test
- Relationship: Often K_t ≈ L_e in SI units
- Effect: Determines current-to-torque conversion

### Thermal Parameters

**R_th - Thermal Resistance** (°C/W)
- Measured with: Heating/cooling curve
- Typical values: 1 - 10 °C/W for small motors
- Effect: Higher R_th → hotter steady-state temperature

**C_th - Thermal Capacitance** (J/°C)
- Measured with: Thermal time constant
- Typical values: 5 - 50 J/°C for small motors
- Effect: Higher C_th → slower temperature changes

## Calibration Strategies

### Manual Tuning (Used in This Lab)

**Procedure**:
1. Start with datasheet/estimated values
2. Run simulation, compare to data
3. Identify which parameter to adjust:
   - Too slow response → decrease J or L
   - Wrong steady-state speed → adjust b or K_t
   - Current mismatch → adjust R or L_e
4. Adjust parameter, re-run
5. Iterate until good fit

**Pros**: Educational, builds intuition
**Cons**: Slow, requires expertise

### Automated Optimization

**Using scipy.optimize**:
```python
from scipy.optimize import minimize

def objective(params_vector):
    # Convert vector to params object
    params = vector_to_params(params_vector)
    # Simulate
    omega_sim = simulate_motor(params, ...)
    # Calculate error
    return calculate_rmse(omega_sim, omega_real)

result = minimize(objective, initial_guess, method='Nelder-Mead')
optimal_params = result.x
```

**Pros**: Fast, finds global minimum
**Cons**: May overfit, requires good initial guess

### Bayesian Calibration

**Using MCMC sampling**:
- Treats parameters as probability distributions
- Accounts for measurement uncertainty
- Provides confidence intervals on predictions
- Advanced topic (not covered in this lab)

## Validation Best Practices

### Data Collection

**Requirements**:
- Multiple operating conditions (different voltages)
- Cover full speed range
- Include transients (startup, shutdown)
- High sampling rate (>100 Hz for small motors)

**Sensors**:
- Voltage: Voltage divider or sensor
- Current: Hall effect sensor or shunt resistor
- Speed: Optical encoder or tachometer

### Validation Metrics

**RMSE** (Root Mean Square Error):
- Overall fit quality
- Same units as measurement
- Sensitive to outliers

**NRMSE** (Normalized RMSE):
- RMSE / (max - min)
- Unitless, easier to compare across systems
- <0.05 = excellent, <0.10 = good

**R²** (Coefficient of Determination):
- Ranges 0 to 1 (1 = perfect)
- How much variance explained
- Can be misleading for biased models

### Cross-Validation

**Holdout Method**:
1. Calibrate on 70% of data
2. Validate on remaining 30%
3. Check if performance similar

**K-Fold**:
- Divide data into K subsets
- Train on K-1, validate on 1
- Repeat K times, average error

## Virtual Sensing Applications

### Temperature Monitoring

**Why It Matters**:
- Motor life decreases exponentially with temperature
- Rule of thumb: Every 10°C increase halves lifespan
- Thermal limits often reached before electrical limits

**Applications**:
- Automotive: Electric vehicle motors
- Industrial: Servo motors in robots
- Aerospace: Actuator health monitoring

**Implementation**:
```python
# Real-time loop
while operating:
    V, i = measure_voltage_and_current()
    T_est = thermal_model.update(V, i, dt)

    if T_est > T_warning:
        reduce_power()
    if T_est > T_critical:
        shutdown()
```

### Other Virtual Sensors

**Torque Estimation**:
```python
T_est = K_t * i - b * omega
```
- No expensive torque sensor needed
- Real-time torque control
- Detect mechanical jams

**Efficiency Estimation**:
```python
P_electrical = V * i
P_mechanical = T_est * omega
efficiency = P_mechanical / P_electrical
```
- Detect bearing wear (efficiency drops)
- Optimize operating point

**Remaining Useful Life**:
- Track cumulative thermal stress
- Predict bearing failure
- Schedule maintenance proactively

## Exercises and Extensions

### Beginner

1. **Parameter Sensitivity**
   - Change R by ±20%, observe effect on current
   - Change J by ±20%, observe effect on acceleration
   - Which parameter has the most impact?

2. **Different Input Profiles**
   - Try sinusoidal voltage: `V(t) = 6 + 6*sin(2π*t)`
   - Try PWM: Square wave at 100 Hz
   - How does frequency affect current ripple?

3. **Thermal Limits**
   - Find voltage that keeps T < 60°C steady-state
   - How long can you run at 24V before overheating?

### Intermediate

4. **Load Variation**
   - Add external load torque `T_load(t)`
   - Modify mechanical equation: `dω/dt = (K_t*i - b*ω - T_load) / J`
   - Simulate motor lifting a weight

5. **Controller Design**
   - Implement PI speed controller
   - Target: ω = 100 rad/s
   - Tune gains for fast response without overshoot

6. **Multi-Parameter Optimization**
   - Use scipy.optimize.minimize to calibrate all parameters
   - Compare manual vs. automated calibration

### Advanced

7. **Non-linear Friction**
   - Replace `b*ω` with Coulomb + viscous: `T_friction = T_c*sign(ω) + b*ω`
   - Observe stick-slip at low speeds

8. **Magnetic Saturation**
   - Make K_t dependent on current: `K_t(i) = K_t0 / (1 + i/i_sat)`
   - Observe torque saturation at high current

9. **Thermal Network**
   - Add multiple thermal nodes (windings, housing, ambient)
   - 3-node network with different R_th between nodes

10. **Real Hardware Integration**
    - Connect to Arduino with motor driver
    - Collect real voltage/current/speed data
    - Calibrate model to your physical motor
    - Compare virtual sensor to thermocouple reading

## Comparison with Other Modeling Approaches

### Physics-Based vs. Data-Driven

| Aspect | Physics-Based (This Lab) | Data-Driven (ML) |
|--------|--------------------------|------------------|
| **Data Needs** | Moderate (calibration) | Large (training) |
| **Interpretability** | High (physical meaning) | Low (black box) |
| **Extrapolation** | Good | Poor |
| **Development Time** | Longer (derive equations) | Shorter (train model) |
| **Accuracy** | Excellent (if physics known) | Variable |
| **Uncertainty** | Well-characterized | Hard to quantify |

**Best Practice**: Hybrid approach
- Physics model for known behaviors
- ML for unmodeled effects (e.g., bearing wear)
- Combine strengths of both

### Comparison with Previous Labs

| Lab | Paradigm | Time | States | Purpose |
|-----|----------|------|--------|---------|
| Lab 2 | DES | Discrete events | Discrete | Operational |
| Lab 3 | ABM | Agent steps | Discrete | Spatial |
| Lab 4 | SD | Continuous (aggregated) | Continuous | Strategic |
| **Lab 5** | **Physics ODE** | **Continuous (detailed)** | **Continuous** | **Control/Monitoring** |

**When to Use Physics ODEs**:
- Detailed physical system understanding needed
- Real-time control applications
- Virtual sensing requirements
- High accuracy critical
- Safety implications

## Troubleshooting

### ODE Solver Issues

**Problem**: "Integration failed" or "step size too small"
- **Cause**: Stiff equations or numerical instability
- **Solution**: Use 'Radau' or 'BDF' methods instead of 'RK45'
```python
solution = solve_ivp(..., method='Radau')
```

**Problem**: Solution oscillates or diverges
- **Cause**: Parameters are unrealistic (negative, too large)
- **Solution**: Check parameter values, use physical constraints

### Calibration Issues

**Problem**: Can't achieve good fit
- Check: Is your model structure correct?
- Check: Do you have enough measurements?
- Try: Different initial parameter guesses
- Consider: Model may be missing physics (e.g., saturation)

**Problem**: Overfitting
- **Symptoms**: Perfect fit to calibration data, poor on test data
- **Cause**: Too many parameters, not enough data
- **Solution**: Reduce model complexity or get more data

### Numerical Accuracy

**Problem**: Results change with tolerances
- Default: rtol=1e-3, atol=1e-6 (usually sufficient)
- For higher accuracy: rtol=1e-6, atol=1e-9
- Trade-off: Accuracy vs. computation time

## Mathematical Formulation

For those interested in the detailed mathematics:

### System Equations

**State vector**: `y = [ω, i, T]ᵀ`

**Dynamics**: `dy/dt = f(y, u, θ)`

Where:
- `u = V(t)` is the control input (voltage)
- `θ = [R, L, J, b, K_t, L_e, R_th, C_th]ᵀ` are parameters

**Explicit form**:
```
dω/dt = (1/J) · (K_t · i - b · ω)

di/dt = (1/L) · (V - R · i - L_e · ω)

dT/dt = (1/C_th) · (R · i² - (T - T_amb) / R_th)
```

### Jacobian (for stiff solvers)

```
J = ∂f/∂y = [
  [-b/J,        K_t/J,    0    ],
  [-L_e/L,      -R/L,     0    ],
  [0,           2Ri/C_th, -1/(R_th·C_th)]
]
```

The electrical subsystem responds faster than mechanical (L << J typically), making this a **mildly stiff** system.

## References

### DC Motor Theory

- **Krishnan, R.** "Electric Motor Drives: Modeling, Analysis, and Control" (2001)
- **Hughes, A. & Drury, B.** "Electric Motors and Drives" (2013)
- Classic textbooks covering motor physics

### Numerical Methods

- **Hairer, E. et al.** "Solving Ordinary Differential Equations" (1993)
  - Comprehensive ODE theory
- **SciPy Documentation**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

### Parameter Identification

- **Ljung, L.** "System Identification: Theory for the User" (1999)
  - Standard reference for calibration

### Digital Twins

- **Glaessgen & Stargel** "The Digital Twin Paradigm for Future NASA and U.S. Air Force Vehicles" (2012)
  - Original Digital Twin concept paper

## Author Notes

This lab demonstrates:
- Physics-based ODE modeling from first principles
- Numerical integration with scipy
- Model calibration workflow
- Virtual sensing capabilities
- Complete Digital Twin development cycle

The DC motor is an ideal educational example because:
- Physics is well-understood
- Equations are manageable (3 ODEs)
- Shows multi-domain coupling
- Relevant to many applications
- Can be validated with hardware

The virtual temperature sensor showcases a key Digital Twin value proposition: estimating quantities that are expensive or impossible to measure directly.

## Next Steps

After completing this lab:
1. Try the exercises (start with parameter sensitivity)
2. Implement a controller using the model
3. Compare different calibration methods
4. If you have hardware, calibrate to a real motor!
5. Explore model-based control (MPC, LQR)
6. Consider hybrid physics-ML approaches

May your ODEs converge smoothly! ⚡🔄
