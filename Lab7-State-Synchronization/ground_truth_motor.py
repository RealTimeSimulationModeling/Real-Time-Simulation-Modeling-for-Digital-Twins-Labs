"""
Lab 7: State Synchronization and Estimation - Ground Truth Generator
======================================================================

Generates a baseline "ground truth" dataset representing the perfect, real-world
behavior of a DC motor. This dataset acts as our physical asset for the subsequent
state estimation lab.

This script simulates a DC motor with known "true" parameters responding to a
dynamic voltage input. The output is saved to a CSV file that will be read by
the sensor publisher.

Prerequisites:
    - numpy
    - scipy
    - pandas

Usage:
    python ground_truth_motor.py

Output:
    - ground_truth.csv: Contains time, voltage, angular_velocity, current
"""

import numpy as np
from scipy.integrate import solve_ivp
import pandas as pd


# ========================================================================================
# TRUE MOTOR PARAMETERS
# ========================================================================================

# These are the "true" physical constants of the real motor.
# These parameters represent the actual physical asset we're trying to model.

TRUE_PARAMS = {
    # Electrical parameters
    'R': 1.0,           # Armature resistance (Ω)
    'L': 0.5,           # Armature inductance (H)
    'L_e': 0.01,        # Back-EMF constant (V·s/rad)

    # Mechanical parameters
    'J': 0.01,          # Rotor inertia (kg·m²)
    'b': 0.1,           # Viscous friction coefficient (N·m·s/rad)
    'K_t': 0.01,        # Torque constant (N·m/A)
}


# ========================================================================================
# DC MOTOR MODEL (GROUND TRUTH)
# ========================================================================================

def dc_motor_model(t, y, voltage_func, params):
    """
    DC motor differential equations (electrical + mechanical coupling).

    This is the same physics-based model from Lab 5, representing the
    true behavior of the physical motor.

    State vector y = [angular_velocity, current]

    Args:
        t: Current time
        y: State vector [omega, i]
        voltage_func: Function that returns voltage at time t
        params: Dictionary of motor parameters

    Returns:
        derivatives: [d_omega/dt, di/dt]
    """
    omega, i = y
    V = voltage_func(t)

    # Extract parameters
    R = params['R']
    L = params['L']
    L_e = params['L_e']
    J = params['J']
    b = params['b']
    K_t = params['K_t']

    # Electrical equation: L * di/dt = V - R*i - L_e*omega
    di_dt = (V - R*i - L_e*omega) / L

    # Mechanical equation: J * d_omega/dt = K_t*i - b*omega
    domega_dt = (K_t*i - b*omega) / J

    return [domega_dt, di_dt]


# ========================================================================================
# VOLTAGE INPUT SIGNAL
# ========================================================================================

def create_voltage_input():
    """
    Create a dynamic voltage input signal for the motor.

    This creates an interesting test signal with steps and ramps to
    demonstrate the motor's dynamic response.

    Returns:
        function: voltage(t) that returns voltage at any time t
    """
    def voltage(t):
        """
        Dynamic voltage profile:
        - 0-2s:    5V (step input, motor spins up)
        - 2-4s:    12V (higher speed)
        - 4-6s:    8V (step down)
        - 6-8s:    Ramp from 8V to 15V
        - 8-10s:   15V (constant high speed)
        - 10-12s:  Ramp down to 0V (coast to stop)
        """
        if t < 2.0:
            return 5.0
        elif t < 4.0:
            return 12.0
        elif t < 6.0:
            return 8.0
        elif t < 8.0:
            # Linear ramp from 8V to 15V over 2 seconds
            return 8.0 + (15.0 - 8.0) * (t - 6.0) / 2.0
        elif t < 10.0:
            return 15.0
        else:
            # Linear ramp from 15V to 0V over 2 seconds
            return 15.0 - 15.0 * (t - 10.0) / 2.0

    return voltage


# ========================================================================================
# SIMULATION
# ========================================================================================

def generate_ground_truth():
    """
    Generate the ground truth dataset by simulating the perfect motor.

    Returns:
        DataFrame: Contains time, voltage, angular_velocity, current
    """
    print("\n" + "="*70)
    print("GROUND TRUTH GENERATOR - DC Motor Simulation")
    print("="*70)

    # Simulation parameters
    t_start = 0.0
    t_end = 12.0
    dt = 0.05  # 50ms time step (20 Hz sampling rate)

    # Initial conditions: motor at rest
    omega_0 = 0.0  # rad/s
    i_0 = 0.0      # A
    y0 = [omega_0, i_0]

    # Create voltage input function
    voltage_func = create_voltage_input()

    print(f"\nSimulation Configuration:")
    print(f"  Time span: {t_start}s to {t_end}s")
    print(f"  Time step: {dt}s ({1/dt:.0f} Hz)")
    print(f"  Initial conditions: ω={omega_0} rad/s, i={i_0} A")
    print(f"\nTrue Motor Parameters:")
    for param, value in TRUE_PARAMS.items():
        print(f"  {param} = {value}")

    # Solve ODE
    print("\nRunning simulation...")

    # Create time points for output
    t_eval = np.arange(t_start, t_end + dt, dt)

    # Solve the differential equations
    solution = solve_ivp(
        fun=lambda t, y: dc_motor_model(t, y, voltage_func, TRUE_PARAMS),
        t_span=(t_start, t_end),
        y0=y0,
        t_eval=t_eval,
        method='RK45',  # Runge-Kutta 4/5 adaptive method
        dense_output=False,
        max_step=dt
    )

    if not solution.success:
        raise RuntimeError(f"Simulation failed: {solution.message}")

    print(f"✓ Simulation completed successfully")
    print(f"  {len(solution.t)} time points generated")

    # Extract results
    time = solution.t
    angular_velocity = solution.y[0]
    current = solution.y[1]

    # Calculate voltage at each time point
    voltage = np.array([voltage_func(t) for t in time])

    # Create DataFrame
    df = pd.DataFrame({
        'time': time,
        'voltage': voltage,
        'angular_velocity': angular_velocity,
        'current': current
    })

    # Display summary statistics
    print(f"\nGround Truth Dataset Summary:")
    print(f"  Time range: [{df['time'].min():.2f}, {df['time'].max():.2f}] seconds")
    print(f"  Voltage range: [{df['voltage'].min():.2f}, {df['voltage'].max():.2f}] V")
    print(f"  Angular velocity range: [{df['angular_velocity'].min():.2f}, {df['angular_velocity'].max():.2f}] rad/s")
    print(f"  Current range: [{df['current'].min():.2f}, {df['current'].max():.2f}] A")

    return df


# ========================================================================================
# MAIN EXECUTION
# ========================================================================================

def main():
    """
    Main function: Generate and save ground truth dataset.
    """
    # Generate the data
    df = generate_ground_truth()

    # Save to CSV
    output_file = 'ground_truth.csv'
    df.to_csv(output_file, index=False)

    print(f"\n✓ Successfully generated {output_file}")
    print(f"  File size: {len(df)} rows × {len(df.columns)} columns")
    print(f"  Columns: {', '.join(df.columns)}")

    print("\n" + "="*70)
    print("Next Steps:")
    print("  1. Run 'python noisy_sensor_publisher.py' to simulate sensor")
    print("  2. Run 'python motor_digital_twin.py' to see state estimation")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
