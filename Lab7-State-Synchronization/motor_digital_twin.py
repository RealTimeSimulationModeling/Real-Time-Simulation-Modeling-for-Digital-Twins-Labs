"""
Lab 7: State Synchronization and Estimation - Motor Digital Twin
==================================================================

Implements the Digital Twin of a DC motor with real-time state estimation.

This is the core of the lab: it demonstrates how an imperfect model can be
continuously corrected by noisy sensor data to produce a highly accurate
state estimate. This is the fundamental principle behind Kalman filters
and modern state estimation techniques.

Key Concepts:
    - Predict-Update Cycle: The twin predicts the next state using its model,
      then updates/corrects this prediction when sensor data arrives
    - Sensor Fusion: Combining model predictions with sensor measurements
    - Model Imperfection: The twin's internal parameters are deliberately wrong
    - Measurement Noise: The sensor data is noisy
    - Optimal Estimation: Despite both limitations, the estimate is accurate

Prerequisites:
    - paho-mqtt library
    - numpy
    - matplotlib
    - Running MQTT broker
    - Running noisy_sensor_publisher.py

Usage:
    1. Terminal 1: mosquitto -v
    2. Terminal 2: python ground_truth_motor.py (if not already done)
    3. Terminal 3: python noisy_sensor_publisher.py
    4. Terminal 4: python motor_digital_twin.py

Observe how the green line ('Digital Twin Estimate') smoothly tracks the true
system behavior by effectively filtering the noise from the red dots ('Noisy
Sensor') and correcting the bias of the blue line ('Model Prediction').
"""

import paho.mqtt.client as mqtt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import queue
import threading
import json
import time
from datetime import datetime
from collections import deque


# ========================================================================================
# CONFIGURATION
# ========================================================================================

# MQTT Configuration
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC = "digital_twin/motor/sensor/angular_velocity"

# Digital Twin Parameters (IMPERFECT MODEL)
# NOTICE: The friction 'b' is deliberately set higher than the true value (0.1)
# This simulates the common real-world scenario where our model is imperfect
TWIN_PARAMS = {
    'R': 1.0,      # Resistance (Ω) - Correct
    'L': 0.5,      # Inductance (H) - Correct
    'L_e': 0.01,   # Back-EMF (V·s/rad) - Correct
    'J': 0.01,     # Inertia (kg·m²) - Correct
    'b': 0.15,     # Friction (N·m·s/rad) - WRONG! True value is 0.1
    'K_t': 0.01,   # Torque constant (N·m/A) - Correct
}

# State Estimation Gain
# This gain (K) determines how much we trust the sensor measurement vs. our model
# K = 0: Ignore sensor, trust model completely (poor for imperfect models)
# K = 1: Ignore model, trust sensor completely (poor for noisy sensors)
# K = 0.1-0.3: Good balance for this scenario
GAIN_K = 0.2

# Simulation Parameters
UPDATE_INTERVAL = 50  # Milliseconds between updates (20 Hz)

# Visualization Parameters
PLOT_HISTORY = 300  # Number of points to display in plot


# ========================================================================================
# MQTT MESSAGE QUEUE
# ========================================================================================

# Thread-safe queue for incoming sensor measurements
# The MQTT callback runs in a separate thread, so we need a queue to safely
# pass messages to the main simulation loop
message_queue = queue.Queue()


# ========================================================================================
# MQTT SUBSCRIBER SETUP
# ========================================================================================

def on_connect(client, userdata, flags, rc):
    """Callback when client connects to broker."""
    if rc == 0:
        print(f"✓ Connected to MQTT broker at {BROKER_ADDRESS}:{PORT}")
        print(f"  Subscribing to topic: {TOPIC}")
        client.subscribe(TOPIC, qos=0)
    else:
        print(f"✗ Connection failed with code {rc}")


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """Callback when subscription is confirmed."""
    print(f"✓ Subscription confirmed (QoS: {granted_qos[0]})")
    print()


def on_message(client, userdata, msg):
    """
    Callback when a message is received.

    Messages are placed in a queue for processing by the main simulation loop.
    This decouples the network thread from the simulation thread.
    """
    try:
        payload_str = msg.payload.decode('utf-8')
        sensor_data = json.loads(payload_str)
        # Put the entire sensor data dictionary into the queue
        message_queue.put(sensor_data)
    except Exception as e:
        print(f"✗ Error processing message: {e}")


# Create MQTT client
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "MotorDigitalTwin")
mqtt_client.on_connect = on_connect
mqtt_client.on_subscribe = on_subscribe
mqtt_client.on_message = on_message


# ========================================================================================
# DIGITAL TWIN CLASS
# ========================================================================================

class MotorDigitalTwin:
    """
    Digital Twin with predict-update state estimation cycle.

    This class maintains an internal model of the motor and continuously
    updates its state estimate based on sensor measurements.
    """

    def __init__(self, params, gain):
        """
        Initialize the Digital Twin.

        Args:
            params: Dictionary of (imperfect) motor parameters
            gain: Kalman-like gain (0 to 1) for sensor fusion
        """
        self.params = params
        self.gain = gain

        # State vector: [angular_velocity, current]
        self.velocity = 0.0  # rad/s
        self.current = 0.0   # A

        # Input
        self.voltage = 0.0   # V

        # Tracking for visualization
        self.last_update_time = time.time()

        # History buffers for plotting
        self.time_history = deque(maxlen=PLOT_HISTORY)
        self.measured_history = deque(maxlen=PLOT_HISTORY)
        self.predicted_history = deque(maxlen=PLOT_HISTORY)
        self.estimated_history = deque(maxlen=PLOT_HISTORY)
        self.true_history = deque(maxlen=PLOT_HISTORY)  # For reference

        # Statistics
        self.message_count = 0
        self.prediction_errors = []
        self.estimation_errors = []

        print("Digital Twin Initialized")
        print(f"  Initial state: ω={self.velocity} rad/s, i={self.current} A")
        print(f"  Estimation gain: K={self.gain}")
        print(f"  Model parameters (IMPERFECT):")
        for param, value in self.params.items():
            print(f"    {param} = {value}")
        print()

    def model_dynamics(self, velocity, current, voltage):
        """
        Calculate the derivatives using the IMPERFECT internal model.

        This is a simplified Euler step calculation, not a full ODE solver.
        It's intentionally simple for educational clarity.

        Args:
            velocity: Current angular velocity (rad/s)
            current: Current armature current (A)
            voltage: Input voltage (V)

        Returns:
            tuple: (d_velocity/dt, d_current/dt)
        """
        # Extract parameters
        R = self.params['R']
        L = self.params['L']
        L_e = self.params['L_e']
        J = self.params['J']
        b = self.params['b']  # This is WRONG (0.15 instead of 0.1)
        K_t = self.params['K_t']

        # Electrical dynamics: di/dt = (V - R*i - L_e*ω) / L
        di_dt = (voltage - R*current - L_e*velocity) / L

        # Mechanical dynamics: dω/dt = (K_t*i - b*ω) / J
        # Because b is too high, this will underestimate velocity
        domega_dt = (K_t*current - b*velocity) / J

        return domega_dt, di_dt

    def predict(self, dt):
        """
        Prediction step: Use internal model to predict next state.

        This is the "predict" in the predict-update cycle.

        Args:
            dt: Time step (seconds)

        Returns:
            float: Predicted angular velocity
        """
        # Calculate derivatives using imperfect model
        domega_dt, di_dt = self.model_dynamics(self.velocity, self.current, self.voltage)

        # Simple Euler integration: state(t+dt) = state(t) + derivative*dt
        predicted_velocity = self.velocity + domega_dt * dt
        predicted_current = self.current + di_dt * dt

        return predicted_velocity, predicted_current

    def update(self, dt):
        """
        Main predict-update cycle for one time step.

        This method:
        1. Predicts the next state using the imperfect model
        2. Checks if a sensor measurement is available
        3. If yes, corrects the prediction using the measurement
        4. If no, uses the prediction as-is

        Args:
            dt: Time step (seconds)

        Returns:
            tuple: (measured_vel, predicted_vel, estimated_vel, true_vel, timestamp)
        """
        # STEP 1: PREDICT using imperfect model
        predicted_velocity, predicted_current = self.predict(dt)

        # STEP 2: CHECK FOR MEASUREMENT
        measured_velocity = None
        true_velocity = None
        timestamp = None

        try:
            # Non-blocking check for sensor data
            sensor_data = message_queue.get_nowait()

            # Extract data
            measured_velocity = sensor_data['measured_velocity']
            self.voltage = sensor_data['voltage']  # Update input voltage
            timestamp = sensor_data['timestamp']
            true_velocity = sensor_data['metadata'].get('true_velocity', None)

            self.message_count += 1

            # STEP 3: UPDATE (Correct prediction with measurement)
            # This is the sensor fusion step
            # Innovation (error between measurement and prediction)
            error = measured_velocity - predicted_velocity

            # Apply Kalman-like correction
            # estimated = predicted + K * (measured - predicted)
            corrected_velocity = predicted_velocity + self.gain * error

            # Update state with corrected value
            self.velocity = corrected_velocity
            self.current = predicted_current  # We only measure velocity, not current

            # Track errors for statistics
            if true_velocity is not None:
                pred_error = abs(predicted_velocity - true_velocity)
                est_error = abs(corrected_velocity - true_velocity)
                self.prediction_errors.append(pred_error)
                self.estimation_errors.append(est_error)

        except queue.Empty:
            # No measurement available, use prediction only
            self.velocity = predicted_velocity
            self.current = predicted_current

        # STEP 4: RECORD FOR VISUALIZATION
        current_time = time.time()
        if timestamp is not None:
            self.time_history.append(timestamp)
        else:
            # If no measurement, extrapolate time
            if len(self.time_history) > 0:
                self.time_history.append(self.time_history[-1] + dt)
            else:
                self.time_history.append(0.0)

        self.measured_history.append(measured_velocity)
        self.predicted_history.append(predicted_velocity)
        self.estimated_history.append(self.velocity)
        self.true_history.append(true_velocity)

        return measured_velocity, predicted_velocity, self.velocity, true_velocity, timestamp


# ========================================================================================
# VISUALIZATION
# ========================================================================================

class RealtimePlotter:
    """
    Real-time matplotlib animation showing the predict-update cycle.
    """

    def __init__(self, twin):
        """
        Initialize the plotter.

        Args:
            twin: MotorDigitalTwin instance
        """
        self.twin = twin

        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(12, 6))

        # Create line objects
        # Noisy sensor (red scatter points)
        self.line_measured, = self.ax.plot([], [], 'r.', label='Noisy Sensor', alpha=0.6, markersize=4)

        # Model prediction - shows the bias from wrong parameters (dashed blue)
        self.line_predicted, = self.ax.plot([], [], 'b--', label='Model Prediction (Biased)', linewidth=2, alpha=0.7)

        # Digital Twin estimate - the corrected state (solid green)
        self.line_estimated, = self.ax.plot([], [], 'g-', label='Digital Twin Estimate', linewidth=2.5)

        # True value - for reference (thin gray line)
        self.line_true, = self.ax.plot([], [], 'k-', label='Ground Truth (Reference)', linewidth=1, alpha=0.3)

        # Configure plot
        self.ax.set_xlabel('Time (s)', fontsize=12)
        self.ax.set_ylabel('Angular Velocity (rad/s)', fontsize=12)
        self.ax.set_title('Digital Twin State Estimation: Predict-Update Cycle\n'
                         'Observe how sensor fusion produces accurate estimates from noisy data and biased model',
                         fontsize=13, fontweight='bold')
        self.ax.legend(loc='upper left', fontsize=10)
        self.ax.grid(True, alpha=0.3)

        # Statistics text
        self.stats_text = self.ax.text(0.02, 0.97, '', transform=self.ax.transAxes,
                                       verticalalignment='top', fontsize=9,
                                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    def init(self):
        """Initialize animation."""
        self.line_measured.set_data([], [])
        self.line_predicted.set_data([], [])
        self.line_estimated.set_data([], [])
        self.line_true.set_data([], [])
        return self.line_measured, self.line_predicted, self.line_estimated, self.line_true

    def update(self, frame):
        """
        Update function called by FuncAnimation.

        Args:
            frame: Frame number (not used, we update based on real time)
        """
        # Get current time
        current_time = time.time()

        # Calculate dt
        dt = UPDATE_INTERVAL / 1000.0  # Convert ms to seconds

        # Run one step of predict-update cycle
        measured, predicted, estimated, true, timestamp = self.twin.update(dt)

        # Update plot data
        times = list(self.twin.time_history)

        # Measured values (only when available)
        measured_vals = [v if v is not None else np.nan for v in self.twin.measured_history]
        self.line_measured.set_data(times, measured_vals)

        # Predicted, estimated, and true values
        self.line_predicted.set_data(times, list(self.twin.predicted_history))
        self.line_estimated.set_data(times, list(self.twin.estimated_history))

        true_vals = [v if v is not None else np.nan for v in self.twin.true_history]
        self.line_true.set_data(times, true_vals)

        # Auto-scale axes
        if len(times) > 0:
            self.ax.set_xlim(max(0, times[-1] - 10), times[-1] + 1)  # Show last 10 seconds

            # Get all non-nan values for y-axis scaling
            all_vals = []
            all_vals.extend([v for v in measured_vals if not np.isnan(v)])
            all_vals.extend(list(self.twin.predicted_history))
            all_vals.extend(list(self.twin.estimated_history))

            if len(all_vals) > 0:
                y_min = min(all_vals)
                y_max = max(all_vals)
                margin = (y_max - y_min) * 0.1
                self.ax.set_ylim(y_min - margin, y_max + margin)

        # Update statistics text
        if len(self.twin.prediction_errors) > 0:
            avg_pred_error = np.mean(self.twin.prediction_errors)
            avg_est_error = np.mean(self.twin.estimation_errors)
            improvement = ((avg_pred_error - avg_est_error) / avg_pred_error) * 100

            stats = f"Messages: {self.twin.message_count}\n"
            stats += f"Avg Model Error: {avg_pred_error:.2f} rad/s\n"
            stats += f"Avg Estimate Error: {avg_est_error:.2f} rad/s\n"
            stats += f"Improvement: {improvement:.1f}%\n"
            stats += f"Gain K: {self.twin.gain}"

            self.stats_text.set_text(stats)

        return self.line_measured, self.line_predicted, self.line_estimated, self.line_true, self.stats_text


# ========================================================================================
# MAIN EXECUTION
# ========================================================================================

def main():
    """
    Main function: Set up MQTT, create Digital Twin, and run visualization.
    """
    print("\n" + "="*70)
    print("DIGITAL TWIN STATE ESTIMATION - Predict-Update Cycle")
    print("="*70)
    print("\nThis simulation demonstrates:")
    print("  • How an IMPERFECT model (wrong friction coefficient)")
    print("  • Combined with NOISY sensor measurements")
    print("  • Produces an ACCURATE state estimate")
    print("  • Through continuous predict-update cycles (sensor fusion)")
    print()

    # Connect to MQTT broker
    try:
        print("Connecting to MQTT broker...")
        mqtt_client.connect(BROKER_ADDRESS, PORT)
        mqtt_client.loop_start()  # Start network loop in background thread
        time.sleep(2)  # Wait for connection

    except Exception as e:
        print(f"\n✗ Failed to connect to broker: {e}")
        print(f"  Is Mosquitto running? Try: mosquitto -v")
        print(f"  Is sensor publisher running? Try: python noisy_sensor_publisher.py")
        return

    # Create Digital Twin
    twin = MotorDigitalTwin(TWIN_PARAMS, GAIN_K)

    # Create plotter
    plotter = RealtimePlotter(twin)

    print("="*70)
    print("Starting real-time visualization...")
    print("Close the plot window to stop.")
    print("="*70)
    print()

    # Run animation
    try:
        ani = animation.FuncAnimation(
            plotter.fig,
            plotter.update,
            init_func=plotter.init,
            interval=UPDATE_INTERVAL,  # Update every 50ms (20 Hz)
            blit=False,
            cache_frame_data=False
        )

        plt.tight_layout()
        plt.show()

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        # Cleanup
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("\n✓ Digital Twin stopped")

        # Display final statistics
        if len(twin.prediction_errors) > 0:
            print("\n" + "="*70)
            print("FINAL STATISTICS")
            print("="*70)
            print(f"Total measurements: {twin.message_count}")
            print(f"\nPrediction Error (imperfect model alone):")
            print(f"  Mean: {np.mean(twin.prediction_errors):.2f} rad/s")
            print(f"  Std:  {np.std(twin.prediction_errors):.2f} rad/s")
            print(f"\nEstimation Error (after sensor fusion):")
            print(f"  Mean: {np.mean(twin.estimation_errors):.2f} rad/s")
            print(f"  Std:  {np.std(twin.estimation_errors):.2f} rad/s")
            improvement = ((np.mean(twin.prediction_errors) - np.mean(twin.estimation_errors))
                          / np.mean(twin.prediction_errors)) * 100
            print(f"\nImprovement: {improvement:.1f}%")
            print("="*70)

        print("\nGoodbye!\n")


# ========================================================================================
# SCRIPT EXECUTION
# ========================================================================================

if __name__ == "__main__":
    main()
