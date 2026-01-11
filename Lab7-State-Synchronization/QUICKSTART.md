# Lab 7: State Synchronization - Quick Start Guide

## What This Lab Does

Demonstrates **sensor fusion** and the **predict-update cycle** - the heart of Digital Twin state estimation.

Shows how an **imperfect model** + **noisy sensor** → **accurate estimate**

---

## 30-Second Concept

**The Problem**:
- Your physics model has wrong parameters (biased)
- Your sensor measurements are noisy (random errors)
- Neither alone is good enough

**The Solution**:
- **Predict** next state using model
- **Update** prediction using sensor measurement
- Repeat continuously
- Result: Smooth AND accurate!

This is a simplified **Kalman Filter**.

---

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install MQTT Broker

**Ubuntu/Debian**:
```bash
sudo apt-get install mosquitto mosquitto-clients
```

**macOS**:
```bash
brew install mosquitto
```

---

## Running the Lab (4 Terminals)

### Terminal 1: Start MQTT Broker
```bash
mosquitto -v
```

### Terminal 2: Generate Ground Truth (one-time)
```bash
cd Lab7-State-Synchronization
python ground_truth_motor.py
```

Expected output:
```
✓ Simulation completed successfully
  241 time points generated

✓ Successfully generated ground_truth.csv
```

### Terminal 3: Start Sensor Publisher
```bash
python noisy_sensor_publisher.py
```

Expected output:
```
✓ Connected to MQTT broker
✓ Loaded 241 data points

Publishing sensor data...

[t=  0.00s] Message #  1
  True velocity:     0.00 rad/s
  Noisy reading:     2.34 rad/s (error:  +2.34)
  Voltage input:     5.00 V
```

### Terminal 4: Start Digital Twin
```bash
python motor_digital_twin.py
```

A matplotlib window opens showing real-time state estimation.

---

## What You'll See

### The Visualization

Four lines on the plot:

1. **Gray line** - Ground truth (reference)
2. **Red dots** - Noisy sensor measurements
3. **Blue dashed line** - Model prediction (BIASED - wrong parameter)
4. **Green solid line** - Digital Twin estimate (sensor fusion)

### Key Observation

**The green line tracks the truth closely**, even though:
- The blue line is wrong (model bias)
- The red dots are noisy

This is **sensor fusion** in action!

### Statistics Box

Shows in real-time:
```
Messages: 150
Avg Model Error: 12.4 rad/s       ← Model alone (blue)
Avg Estimate Error: 2.8 rad/s     ← After fusion (green)
Improvement: 77%                   ← Power of sensor fusion!
Gain K: 0.2
```

---

## Understanding the Results

### Why Model Alone Fails

The Digital Twin's friction parameter is **deliberately wrong**:
- True value: `b = 0.1`
- Twin's value: `b = 0.15` (50% too high!)

This causes systematic bias:
- Underestimates velocity during acceleration
- Overestimates deceleration
- Blue line drifts away from truth

### Why Sensor Alone Fails

Measurements have Gaussian noise:
- Standard deviation: `σ = 5.0 rad/s`
- Causes ±10-15 rad/s scatter
- Too jumpy for control

### Why Fusion Works

**Model contributes**:
- Smoothness (physics-based constraints)
- Continuity (no sudden jumps)
- Extrapolation (works between measurements)

**Sensor contributes**:
- Ground truth (unbiased on average)
- Bias correction (fixes model errors)
- Drift prevention (anchors to reality)

**Result**: Smooth + Accurate!

---

## The Predict-Update Cycle

What happens in `motor_digital_twin.py`:

```
Every 50ms (20 Hz):

1. PREDICT:
   predicted_velocity = current_velocity + model_dynamics(...) * dt
   [Uses IMPERFECT model]

2. CHECK FOR MEASUREMENT:
   If sensor data available via MQTT:

3. UPDATE:
   error = measured_velocity - predicted_velocity
   corrected_velocity = predicted_velocity + K * error
   [K = 0.2, the "Kalman gain"]

4. VISUALIZE:
   Plot all three: measured, predicted, corrected
```

### The Gain Parameter (K)

`K = 0.2` means:
- Trust model 80%
- Trust sensor 20%

Try modifying `GAIN_K` in the code:
- `K = 0.05`: Smoother, but retains model bias
- `K = 0.5`: Faster correction, but noisier
- `K = 0.2`: Balanced (recommended)

---

## Common Issues

| Problem | Solution |
|---------|----------|
| No plot appears | Ensure matplotlib is installed, try `export MPLBACKEND=TkAgg` |
| Green line equals blue line | Verify sensor publisher is running |
| "Connection refused" | Start Mosquitto first: `mosquitto -v` |
| "ground_truth.csv not found" | Run `python ground_truth_motor.py` first |
| Sensor finishes before twin ready | Start twin first, then publisher |

---

## Quick Experiments

### Experiment 1: Change Noise Level

In `noisy_sensor_publisher.py`:
```python
NOISE_STD_DEV = 10.0  # Increase noise (was 5.0)
```

**Result**: Red dots more scattered, but green line still tracks well!

### Experiment 2: Fix the Model

In `motor_digital_twin.py`:
```python
TWIN_PARAMS = {
    # ...
    'b': 0.1,  # Correct value (was 0.15)
}
```

**Result**: Blue line matches truth. Green line provides smoothing.

### Experiment 3: Adjust Gain

In `motor_digital_twin.py`:
```python
GAIN_K = 0.5  # More aggressive (was 0.2)
```

**Result**: Faster response to measurements, but noisier estimate.

---

## What's Happening Under the Hood

### Ground Truth Generator

```python
# Solve DC motor ODEs with TRUE parameters
solution = solve_ivp(dc_motor_model, ...)

# Save to CSV
df.to_csv('ground_truth.csv')
# Columns: time, voltage, angular_velocity, current
```

### Sensor Publisher

```python
for row in df.iterrows():
    true_velocity = row['angular_velocity']

    # Add noise
    measured = true_velocity + np.random.normal(0, 5.0)

    # Publish via MQTT
    client.publish(TOPIC, json.dumps({
        'measured_velocity': measured,
        'voltage': row['voltage'],
        'timestamp': row['time']
    }))

    time.sleep(...)  # Real-time pacing
```

### Digital Twin

```python
class MotorDigitalTwin:
    def update(self, dt):
        # PREDICT with imperfect model
        predicted_vel = self.velocity + self.model_dynamics(...) * dt

        # UPDATE with sensor (if available)
        if message_queue.has_data():
            measured_vel = message_queue.get()
            error = measured_vel - predicted_vel
            self.velocity = predicted_vel + GAIN_K * error
        else:
            self.velocity = predicted_vel

        return measured_vel, predicted_vel, self.velocity
```

---

## Key Equations

### Euler Integration (Predict)
```
ω(t+Δt) = ω(t) + (dω/dt) * Δt

where dω/dt = (K_t*i - b*ω) / J
```

### Sensor Fusion (Update)
```
error = measured - predicted

corrected = predicted + K * error

where:
  K = 0.2 (fixed gain)

This is equivalent to:
  corrected = 0.8 * predicted + 0.2 * measured
```

---

## Performance Metrics

**Typical Results**:

| Metric | Value | Meaning |
|--------|-------|---------|
| Model Error | 10-15 rad/s | How wrong the blue line is |
| Sensor Noise | ~5 rad/s | Standard deviation of red dots |
| Estimate Error | 2-4 rad/s | How close green is to truth |
| Improvement | 70-80% | Error reduction from fusion |

**Interpretation**: Sensor fusion reduces error by ~75% compared to model alone!

---

## Real-World Analogy

**Driving a car**:

- **Model** (physics): "If I'm going 60 mph and accelerate for 3s, I'll be at mile marker 103"
  - Smooth prediction
  - But: Ignores wind, hills, tire pressure
  - Gets gradually wrong

- **Sensor** (GPS): "You are at mile marker 102.4"
  - Accurate on average
  - But: Jumpy, updates delayed, tunnels cause gaps

- **Fusion** (GPS + inertial): "I'm at 102.6"
  - Uses physics between GPS updates
  - Corrects physics errors when GPS arrives
  - Smooth AND accurate

This is how your phone does navigation!

---

## Next Steps

1. **Read the full README.md** for:
   - Detailed theory (Kalman Filter mathematics)
   - Extension ideas (multi-sensor, parameter estimation)
   - Real-world applications
   - Troubleshooting guide

2. **Try the experiments** above:
   - Modify noise levels
   - Adjust gain
   - Fix/break the model

3. **Integrate with other labs**:
   - Add estimation to DC Motor Twin (Lab 5)
   - Combine with MQTT patterns (Lab 6)

4. **Explore advanced topics**:
   - Full Kalman Filter with adaptive gain
   - Extended Kalman Filter (EKF) for nonlinear systems
   - Multi-sensor fusion

---

## Summary

You've implemented the **fundamental algorithm** of Digital Twin state synchronization:

✅ Generated perfect ground truth
✅ Simulated noisy sensor measurements
✅ Built imperfect physics model
✅ Implemented predict-update cycle
✅ Achieved accurate state estimation through sensor fusion
✅ Visualized the results in real-time

**Key Insight**: Imperfect model + Noisy sensor → Accurate estimate (via fusion)

This is **production technology** used in:
- Autonomous vehicles
- Spacecraft navigation
- Manufacturing quality control
- Robotics and drones
- Battery management systems

**You now understand the heart of Digital Twin synchronization!**

---

For detailed explanations, see **README.md**.
