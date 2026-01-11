# Lab 7: State Synchronization and Estimation

## Overview

This lab demonstrates the **heart of Digital Twin technology**: real-time state synchronization through sensor fusion. You'll implement a simplified version of the **Kalman Filter's predict-update cycle**, showing how an imperfect model combined with noisy sensor data can produce highly accurate state estimates.

### The Core Challenge

In the real world, Digital Twins face two fundamental problems:
1. **Models are never perfect** - Parameters drift, physics is simplified, unknowns exist
2. **Sensors are always noisy** - Electrical noise, quantization, interference

Neither source alone is trustworthy. But **together**, they can produce excellent estimates.

### Learning Objectives

By the end of this lab, you will understand:

1. **The Predict-Update Cycle**
   - Model-based prediction (forward simulation)
   - Measurement-based correction (sensor fusion)
   - Continuous synchronization loop

2. **Sensor Fusion Fundamentals**
   - Combining complementary information sources
   - Balancing trust between model and sensor
   - The role of the Kalman gain

3. **State Estimation in Practice**
   - Handling model imperfection
   - Filtering measurement noise
   - Real-time operation constraints

4. **Digital Twin Architecture**
   - Ground truth generation
   - Noisy sensor simulation
   - Asynchronous MQTT communication
   - Live visualization of estimation performance

---

## Architecture

```
┌──────────────────────────┐
│  Ground Truth Generator  │
│  ground_truth_motor.py   │
│                          │
│  "Perfect" DC motor      │
│  Generates CSV dataset   │
└────────────┬─────────────┘
             │
             ▼
      ground_truth.csv
             │
             ▼
┌──────────────────────────┐
│   Noisy Sensor           │
│   Publisher              │
│                          │
│   Reads CSV              │
│   + Adds noise           │
│   Publishes via MQTT     │
└────────────┬─────────────┘
             │ MQTT
             │ Topic: digital_twin/motor/sensor/angular_velocity
             │ Payload: {measured_velocity, voltage, timestamp}
             ▼
┌──────────────────────────┐
│   Digital Twin           │
│   motor_digital_twin.py  │
│                          │
│   IMPERFECT internal     │
│   model + Sensor data    │
│   → State estimate       │
│                          │
│   Live visualization     │
└──────────────────────────┘
```

### Data Flow

1. **Ground Truth** (`ground_truth_motor.py`):
   - Simulates a "perfect" DC motor using correct physics
   - Generates a CSV file with true behavior
   - Represents the real physical asset

2. **Noisy Sensor** (`noisy_sensor_publisher.py`):
   - Reads ground truth CSV row by row
   - Adds Gaussian noise (σ = 5.0 rad/s)
   - Publishes via MQTT in real-time
   - Simulates a real-world encoder/tachometer

3. **Digital Twin** (`motor_digital_twin.py`):
   - Runs an IMPERFECT internal model (wrong friction parameter)
   - Receives noisy measurements asynchronously
   - Executes predict-update cycle at 20 Hz
   - Displays real-time estimate vs. prediction vs. measurement

---

## The Predict-Update Cycle

This is the fundamental algorithm of modern state estimation:

```python
# INITIALIZATION
state = initial_guess
model_params = imperfect_parameters

while True:
    # PREDICT STEP
    # Use physics model to predict next state
    predicted_state = state + model_dynamics(state) * dt

    # UPDATE STEP
    # If sensor measurement is available:
    if measurement_available:
        # Calculate innovation (error)
        error = measured_value - predicted_state

        # Apply correction with gain K (0 < K < 1)
        corrected_state = predicted_state + K * error

        state = corrected_state
    else:
        state = predicted_state
```

### Why It Works

**Model alone**: Biased by wrong parameters, but smooth and physically consistent

**Sensor alone**: Noisy and jumpy, but unbiased (on average)

**Combined**: The model provides smoothness and physics, the sensor provides correction. The result is smooth AND accurate!

### The Kalman Gain (K)

The gain `K` determines the balance:
- `K = 0`: Ignore sensor completely (bad for imperfect models)
- `K = 1`: Ignore model completely (bad for noisy sensors)
- `K = 0.2` (our value): Trust model 80%, sensor 20%

In full Kalman Filters, K is calculated adaptively based on model and measurement uncertainties. Here, we use a fixed value for simplicity.

---

## Implementation Details

### 1. Ground Truth Generator

**Purpose**: Create the "real world" baseline

**Key Parameters** (TRUE_PARAMS):
```python
{
    'R': 1.0,      # Resistance (Ω)
    'L': 0.5,      # Inductance (H)
    'J': 0.01,     # Inertia (kg·m²)
    'b': 0.1,      # Friction (N·m·s/rad) - TRUE VALUE
    'K_t': 0.01,   # Torque constant (N·m/A)
    'L_e': 0.01,   # Back-EMF constant (V·s/rad)
}
```

**Voltage Profile**:
- 0-2s: 5V (initial spin-up)
- 2-4s: 12V (higher speed)
- 4-6s: 8V (step down)
- 6-8s: Ramp 8V → 15V
- 8-10s: 15V (high speed)
- 10-12s: Ramp 15V → 0V (coast down)

**Output**: `ground_truth.csv` with columns:
- `time`: Simulation time (s)
- `voltage`: Input voltage (V)
- `angular_velocity`: True velocity (rad/s)
- `current`: Armature current (A)

### 2. Noisy Sensor Publisher

**Purpose**: Simulate a real-world sensor with measurement noise

**Noise Model**:
```python
measured_value = true_value + random.normal(0, 5.0)
```

Gaussian (normal) noise with:
- Mean: 0 (unbiased)
- Standard deviation: 5.0 rad/s

This represents a moderately noisy sensor, typical of low-cost encoders.

**Timing**: Publishes data in real-time, synchronized to the CSV timestamps. Uses `time.sleep()` to pace the data stream.

**MQTT Payload**:
```json
{
  "timestamp": 2.35,
  "sensor_id": "VELOCITY_ENCODER_001",
  "measured_velocity": 47.3,
  "voltage": 12.0,
  "metadata": {
    "true_velocity": 42.1,
    "noise_std_dev": 5.0,
    "unit": "rad/s"
  }
}
```

### 3. Digital Twin with State Estimation

**Purpose**: Demonstrate predict-update cycle

**Imperfect Model** (TWIN_PARAMS):
```python
{
    # ... same as TRUE_PARAMS, except:
    'b': 0.15,  # WRONG! True value is 0.1
}
```

The friction coefficient is 50% too high. This causes the model to:
- Underestimate velocity during acceleration
- Overestimate deceleration
- Have a systematic bias

**Predict Step** (Euler Integration):
```python
def predict(self, dt):
    # Calculate derivatives using IMPERFECT model
    domega_dt = (K_t*i - b*omega) / J  # b is WRONG
    di_dt = (V - R*i - L_e*omega) / L

    # Forward Euler step
    predicted_velocity = velocity + domega_dt * dt
    predicted_current = current + di_dt * dt

    return predicted_velocity, predicted_current
```

**Update Step** (Sensor Fusion):
```python
def update(self, measured_velocity):
    # Calculate innovation
    error = measured_velocity - predicted_velocity

    # Correct prediction
    corrected_velocity = predicted_velocity + GAIN_K * error

    return corrected_velocity
```

**Visualization**:
- **Red dots**: Noisy sensor measurements (scatter)
- **Blue dashed line**: Model prediction (biased, smooth)
- **Green solid line**: Digital Twin estimate (accurate, smooth)
- **Gray line**: Ground truth (reference)

**Expected Outcome**:
- Blue line diverges from truth (wrong parameter)
- Red dots scattered around truth (noise)
- Green line tracks truth closely (sensor fusion works!)

---

## Running the Lab

### Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Mosquitto**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mosquitto mosquitto-clients

   # macOS
   brew install mosquitto
   ```

### Step-by-Step Execution

You'll need **four terminal windows**:

**Terminal 1 - MQTT Broker**:
```bash
mosquitto -v
```

**Terminal 2 - Generate Ground Truth** (one-time):
```bash
cd Lab7-State-Synchronization
python ground_truth_motor.py
```

Expected output:
```
======================================================================
GROUND TRUTH GENERATOR - DC Motor Simulation
======================================================================

Simulation Configuration:
  Time span: 0.0s to 12.0s
  Time step: 0.05s (20 Hz)

✓ Simulation completed successfully
  241 time points generated

✓ Successfully generated ground_truth.csv
```

**Terminal 3 - Start Sensor Publisher**:
```bash
python noisy_sensor_publisher.py
```

Expected output:
```
NOISY SENSOR PUBLISHER - Simulated Motor Velocity Sensor
✓ Connected to MQTT broker
✓ Loaded 241 data points

Publishing sensor data...

[t=  0.00s] Message #  1
  True velocity:     0.00 rad/s
  Noisy reading:     2.34 rad/s (error:  +2.34)
  Voltage input:     5.00 V
  Status: ✓ Published
```

**Terminal 4 - Start Digital Twin**:
```bash
python motor_digital_twin.py
```

Expected output:
```
DIGITAL TWIN STATE ESTIMATION - Predict-Update Cycle

This simulation demonstrates:
  • How an IMPERFECT model (wrong friction coefficient)
  • Combined with NOISY sensor measurements
  • Produces an ACCURATE state estimate
  • Through continuous predict-update cycles (sensor fusion)

✓ Connected to MQTT broker
✓ Subscription confirmed

Digital Twin Initialized
  Initial state: ω=0.0 rad/s, i=0.0 A
  Estimation gain: K=0.2
  Model parameters (IMPERFECT):
    b = 0.15

Starting real-time visualization...
```

A matplotlib window opens showing the real-time state estimation.

---

## Understanding the Visualization

### The Plot

**Four lines displayed**:

1. **Gray line** (Ground Truth):
   - The "true" motor behavior from `ground_truth.csv`
   - This is what we're trying to track
   - Shown for reference only (not available to the twin in practice)

2. **Red dots** (Noisy Sensor):
   - The measurements from `noisy_sensor_publisher.py`
   - Scattered around the truth due to noise (σ = 5.0 rad/s)
   - Individually unreliable, but unbiased on average

3. **Blue dashed line** (Model Prediction):
   - The twin's internal model prediction BEFORE correction
   - Smooth, but systematically wrong (biased by incorrect friction)
   - Shows what would happen if we ignored the sensor

4. **Green solid line** (Digital Twin Estimate):
   - The final state estimate AFTER sensor fusion
   - Combines model smoothness with sensor accuracy
   - **This is the power of the predict-update cycle!**

### Statistics Box

Displayed in real-time:
- **Messages**: Number of sensor readings received
- **Avg Model Error**: Mean error of blue line (model alone)
- **Avg Estimate Error**: Mean error of green line (sensor fusion)
- **Improvement**: Percentage reduction in error
- **Gain K**: The sensor fusion gain (0.2)

**Typical Results**:
- Model Error: ~10-15 rad/s (systematic bias)
- Estimate Error: ~2-4 rad/s (mainly residual noise)
- Improvement: ~70-80%

---

## Key Observations

### 1. Model Bias is Corrected

The blue line (prediction) has a **systematic offset** because the friction parameter is wrong. The green line (estimate) **does not** have this bias, even though it uses the same imperfect model internally. The sensor corrects the bias.

### 2. Sensor Noise is Filtered

The red dots are very noisy (σ = 5.0 rad/s). The green line is smooth. The model provides a physical constraint that filters out physically impossible fluctuations.

### 3. The Best of Both Worlds

- Model provides: Smoothness, physical consistency, extrapolation
- Sensor provides: Ground truth, bias correction, drift prevention
- Combined: Smooth AND accurate

### 4. The Importance of Gain Tuning

Try modifying `GAIN_K` in `motor_digital_twin.py`:

**K = 0.05** (trust model more):
- Very smooth estimate
- But retains more model bias
- Slower to respond to sensor corrections

**K = 0.5** (trust sensor more):
- Faster bias correction
- But noisier estimate
- More reactive to measurements

**K = 0.2** (balanced):
- Good compromise
- Reasonably smooth
- Effective bias correction

### 5. Real-Time Operation

The whole system runs in real-time with:
- MQTT asynchronous communication
- Thread-safe message queuing
- 20 Hz update rate (50ms intervals)
- Live matplotlib visualization

This demonstrates production-ready architecture for Digital Twins.

---

## Extension Ideas

### 1. Implement Full Kalman Filter

Replace the fixed gain `K` with an adaptive calculation:

```python
# Add uncertainty tracking
P = process_noise_covariance  # Model uncertainty
R = measurement_noise_covariance  # Sensor uncertainty

# Predict step
P_predicted = P + Q  # Q = process noise

# Update step
K = P_predicted / (P_predicted + R)  # Kalman gain
P = (1 - K) * P_predicted
```

This automatically adjusts trust based on relative uncertainties.

### 2. Multi-Sensor Fusion

Add a second sensor (e.g., current measurement):

```python
# Fuse both velocity and current
error_velocity = measured_velocity - predicted_velocity
error_current = measured_current - predicted_current

corrected_velocity = predicted_velocity + K_v * error_velocity
corrected_current = predicted_current + K_i * error_current
```

### 3. Parameter Estimation

Instead of just estimating state, also estimate the wrong parameter:

```python
# Augmented state: [velocity, current, friction_b]
# The twin learns the true friction value over time
b_estimated = b_estimated + K_param * persistent_error
```

This is called **joint state-parameter estimation**.

### 4. Outlier Rejection

Add robustness to bad measurements:

```python
# Chi-squared test for outliers
if abs(error) > 3 * sigma:
    # Reject this measurement, use prediction only
    state = predicted_state
else:
    # Normal update
    state = predicted_state + K * error
```

### 5. Delayed Measurements

Simulate communication delays:

```python
# Add timestamp to measurements
# Buffer predictions
# When measurement arrives, apply correction retroactively
# This is common in networked systems
```

### 6. Model Switching

Use different models based on operating conditions:

```python
if voltage < 1.0:
    # Use simplified model (coasting)
else:
    # Use full model (driven)
```

---

## Theoretical Background

### The Kalman Filter

This lab implements a simplified Kalman Filter. The full algorithm (1960, Rudolf Kalman) is:

**Predict**:
```
x̂ₖ|ₖ₋₁ = F·x̂ₖ₋₁ + B·uₖ    (state prediction)
Pₖ|ₖ₋₁ = F·Pₖ₋₁·Fᵀ + Q      (covariance prediction)
```

**Update**:
```
Kₖ = Pₖ|ₖ₋₁·Hᵀ·(H·Pₖ|ₖ₋₁·Hᵀ + R)⁻¹  (Kalman gain)
x̂ₖ = x̂ₖ|ₖ₋₁ + Kₖ·(zₖ - H·x̂ₖ|ₖ₋₁)     (state update)
Pₖ = (I - Kₖ·H)·Pₖ|ₖ₋₁                 (covariance update)
```

Where:
- `x̂`: State estimate
- `P`: Error covariance (uncertainty)
- `F`: State transition model
- `H`: Observation model
- `Q`: Process noise covariance
- `R`: Measurement noise covariance
- `K`: Kalman gain (optimal)

Our lab simplifies this to its essence while demonstrating the core concept.

### Why It's Optimal

The Kalman Filter is **provably optimal** for linear systems with Gaussian noise:
- Minimizes mean squared error
- Provides uncertainty quantification
- Recursively updateable (O(1) per step)

For nonlinear systems, use:
- **EKF** (Extended Kalman Filter): Linearize around current estimate
- **UKF** (Unscented Kalman Filter): Sigma-point sampling
- **Particle Filter**: Monte Carlo methods

### Applications in Digital Twins

State estimation is used in:

1. **Manufacturing**: Track tool wear, predict failures
2. **Aerospace**: Estimate aircraft state from GPS+IMU
3. **Automotive**: Fuse camera, radar, lidar for autonomous driving
4. **Energy**: Estimate battery state of charge
5. **Robotics**: Localization and mapping (SLAM)
6. **Healthcare**: Patient vital sign filtering

Essentially, **any system** where you have:
- A physics model (even imperfect)
- Noisy measurements
- Need for real-time state knowledge

---

## Troubleshooting

### No visualization appears

**Problem**: matplotlib window doesn't open

**Solutions**:
- Check X11/display is available
- Try adding `export MPLBACKEND=TkAgg` before running
- Verify matplotlib is installed: `pip show matplotlib`

### Estimate doesn't improve over prediction

**Problem**: Green line overlaps blue line

**Solutions**:
- Verify sensor publisher is running and sending data
- Check MQTT messages are being received (see terminal output)
- Increase `GAIN_K` (e.g., to 0.3) for more aggressive correction
- Verify message_queue is not empty

### Estimate is too noisy

**Problem**: Green line is jumpy like red dots

**Solutions**:
- Decrease `GAIN_K` (e.g., to 0.1) to trust model more
- Reduce `NOISE_STD_DEV` in sensor publisher
- Increase update rate (decrease `UPDATE_INTERVAL`)

### Sensor publisher finishes before twin starts

**Problem**: Twin shows no data

**Solutions**:
- Start twin BEFORE sensor publisher
- Or regenerate ground truth and restart publisher
- The twin can start late and catch the stream mid-way

### MQTT connection errors

**Problem**: "Connection refused"

**Solutions**:
- Verify Mosquitto is running: `ps aux | grep mosquitto`
- Check port 1883 is available: `netstat -an | grep 1883`
- Try restarting broker: `sudo systemctl restart mosquitto`

---

## Key Takeaways

1. **Models + Sensors = Better Than Either Alone**
   - Imperfect models have bias but are smooth
   - Noisy sensors are unbiased but jumpy
   - Fusion gives smooth and accurate estimates

2. **The Predict-Update Cycle is Universal**
   - Predict using model
   - Update using measurement
   - This pattern appears everywhere in estimation

3. **Gain Tuning is Critical**
   - Balance model trust vs. sensor trust
   - Depends on relative uncertainties
   - Can be fixed or adaptive (Kalman Filter)

4. **Real-Time is Achievable**
   - Kalman-type estimators are O(n²) for state dimension n
   - For small systems, easily run at kHz rates
   - Asynchronous measurements handled naturally

5. **This is Production Technology**
   - Used in billions of devices
   - Critical for autonomous systems
   - Foundation of modern control

---

## Next Steps

With state estimation mastered, you can:

1. **Combine with Previous Labs**:
   - Add state estimation to DC motor twin (Lab 5)
   - Estimate queue lengths in coffee shop (Lab 2)
   - Track AGV positions with GPS noise (Lab 3)

2. **Explore Advanced Filters**:
   - Extended Kalman Filter (EKF) for nonlinear systems
   - Unscented Kalman Filter (UKF) for highly nonlinear
   - Particle Filters for non-Gaussian noise

3. **Real Hardware Integration**:
   - Connect to Arduino with real encoder
   - Use actual motor and measure true performance
   - Compare simulation vs. reality

4. **Add Control**:
   - Use estimated state for feedback control
   - Model Predictive Control (MPC)
   - Separation principle: Estimate + Control

---

## References

### Kalman Filtering
- Kalman, R.E. (1960). "A New Approach to Linear Filtering and Prediction Problems"
- Welch, G. & Bishop, G. "An Introduction to the Kalman Filter" (UNC-Chapel Hill TR)
- Simon, D. (2006). "Optimal State Estimation: Kalman, H∞, and Nonlinear Approaches"

### Digital Twin State Synchronization
- Glaessgen, E. & Stargel, D. (2012). "The Digital Twin Paradigm for Future NASA and U.S. Air Force Vehicles"
- Tao, F. et al. (2019). "Digital Twin Driven Prognostics and Health Management"
- Kritzinger, W. et al. (2018). "Digital Twin in Manufacturing: A Categorical Literature Review"

### Sensor Fusion
- Hall, D.L. & Llinas, J. (2001). "Handbook of Multisensor Data Fusion"
- Gustafsson, F. (2010). "Particle Filter Theory and Practice with Positioning Applications"

---

## Summary

This lab demonstrated the **core technology of Digital Twin state synchronization**: the predict-update cycle.

You saw firsthand how:
- An **imperfect physics model** (wrong friction)
- Combined with **noisy sensor data** (σ = 5.0 rad/s)
- Produces **accurate state estimates** through sensor fusion

You implemented:
- Ground truth generation (perfect simulation)
- Noisy sensor simulation (Gaussian noise)
- Digital Twin with predict-update cycle (sensor fusion)
- Real-time MQTT communication
- Live visualization of estimation performance

You learned:
- The fundamental algorithm of Kalman filtering
- How to balance model trust vs. sensor trust
- Why sensor fusion outperforms either source alone
- How to implement real-time state estimation

**This is production technology** used in aerospace, automotive, manufacturing, and robotics worldwide.

**Congratulations on mastering Digital Twin state synchronization!**
