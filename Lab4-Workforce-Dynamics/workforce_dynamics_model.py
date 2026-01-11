"""
Lab 4: Modeling Workforce Dynamics - System Dynamics
====================================================

This script implements a System Dynamics (SD) model of a project-based company's
workforce from first principles, demonstrating stocks, flows, and feedback loops.

System Dynamics Concepts Demonstrated:
    - Stocks: State variables that accumulate over time
    - Flows: Rates that change stocks
    - Feedback Loops: Reinforcing and balancing loops
    - Non-linear Relationships: Pressure effects on productivity and quitting
    - Time Delays: Hiring and burnout delays
    - Overshoot Archetype: Aggressive policy leading to unintended consequences

Implementation Approach:
    - Built from scratch using Euler integration (no specialized SD libraries)
    - Simple for-loop time-stepping makes the mechanics transparent
    - Pure Python + matplotlib for visualization

Scenario:
    1. Company starts in equilibrium (100 employees, 500 project backlog)
    2. Month 6: Big contract arrives (shock: +400 projects)
    3. Company responds with aggressive hiring
    4. Observe unintended consequences: burnout, turnover, productivity collapse

Expected Outcome:
    Classic "overshoot" behavior - aggressive hiring initially helps but creates
    schedule pressure, leading to burnout, high turnover, and potential collapse.
"""

import matplotlib.pyplot as plt
import numpy as np

# ========================================================================================
# PHASE 1: MODEL SETUP AND EQUATIONS
# ========================================================================================

# Simulation Configuration
# -------------------------
SIMULATION_MONTHS = 36  # Run for 3 years
DT = 1.0               # Time step: 1 month
TIME_SHOCK = 6         # Month when big contract arrives

# Initial Stock Values (State Variables)
# ---------------------------------------
# These are the "accumulators" that define the system state
INITIAL_WORKFORCE = 100
INITIAL_BACKLOG = 500

# Model Constants (Parameters)
# -----------------------------
# These govern the relationships between variables

# Productivity Constants
NOMINAL_PRODUCTIVITY = 3.0       # Projects completed per person per month (baseline)
NOMINAL_SCHEDULE_PRESSURE = 5.0  # Expected projects per person (equilibrium)

# Workforce Dynamics Constants
NORMAL_QUIT_RATE_FRACTION = 0.05  # 5% annual turnover = 0.004167/month
TIME_TO_ADJUST_HIRING = 3.0       # Months to close hiring gap
PROJECTS_PER_DESIRED_EMPLOYEE = 5.0  # Used to calculate desired workforce

# External Input
# For equilibrium: new_projects_rate must equal completion_rate
# completion_rate = workforce * productivity = 100 * 3.0 = 300/month at equilibrium
NEW_PROJECTS_RATE = 300.0  # New projects arriving per month (steady state)
SHOCK_SIZE = 1200          # Additional projects from big contract (4 months of work!)


# ========================================================================================
# PHASE 1: SYSTEM EQUATIONS (Non-linear Relationships & Feedback)
# ========================================================================================

def calculate_schedule_pressure(backlog, workforce):
    """
    Calculate workload pressure: projects per employee.

    This is the KEY DRIVER of system behavior. It creates the feedback loops:
    - High pressure → lower productivity → backlog grows → even higher pressure (R)
    - High pressure → more quitting → fewer workers → even higher pressure (R)
    - High pressure → more hiring → more workers → lower pressure (B)

    Args:
        backlog: Number of projects waiting
        workforce: Number of employees

    Returns:
        Projects per person (pressure metric)
    """
    if workforce <= 0:
        return 999.0  # Extreme pressure if no workforce!
    return backlog / workforce


def calculate_effect_of_pressure_on_productivity(pressure):
    """
    Non-linear relationship: How schedule pressure affects productivity.

    This captures the "Yerkes-Dodson Law" - moderate pressure helps, but
    too much pressure crushes productivity.

    Relationship:
        - Pressure = 3-4: Effect = 1.1 (slight boost from urgency)
        - Pressure = 5: Effect = 1.0 (nominal/baseline)
        - Pressure = 7: Effect = 0.85 (starting to struggle)
        - Pressure = 10: Effect = 0.6 (significant degradation)
        - Pressure = 15+: Effect = 0.4 (crisis mode, very inefficient)

    Args:
        pressure: Schedule pressure (projects per person)

    Returns:
        Multiplier on nominal productivity (1.0 = baseline)
    """
    # Using a simple piecewise function for clarity
    if pressure <= 3.0:
        return 1.1  # Light workload, people are focused and efficient
    elif pressure <= 5.0:
        # Linear interpolation from 1.1 to 1.0
        return 1.1 - (pressure - 3.0) * 0.05
    elif pressure <= 7.0:
        # Linear decrease from 1.0 to 0.85
        return 1.0 - (pressure - 5.0) * 0.075
    elif pressure <= 10.0:
        # Steeper decline from 0.85 to 0.6
        return 0.85 - (pressure - 7.0) * 0.0833
    else:
        # Very high pressure: severe degradation
        # Asymptotically approaches 0.3
        return max(0.3, 0.6 - (pressure - 10.0) * 0.04)


def calculate_effect_of_pressure_on_quitting(pressure):
    """
    Non-linear relationship: How schedule pressure affects turnover.

    This creates the REINFORCING BURNOUT SPIRAL:
    High pressure → more quitting → fewer workers → even higher pressure

    Relationship:
        - Pressure = 5 or less: Effect = 1.0 (normal turnover)
        - Pressure = 7: Effect = 1.5 (50% increase in quitting)
        - Pressure = 10: Effect = 3.0 (triple the quit rate!)
        - Pressure = 15: Effect = 6.0 (exodus!)

    Args:
        pressure: Schedule pressure (projects per person)

    Returns:
        Multiplier on normal quit rate (1.0 = baseline)
    """
    if pressure <= NOMINAL_SCHEDULE_PRESSURE:
        return 1.0  # Normal turnover when pressure is manageable
    else:
        # Exponential increase in quitting as pressure rises
        excess_pressure = pressure - NOMINAL_SCHEDULE_PRESSURE
        # For every 2 points of excess pressure, double the quit rate
        return 1.0 * (2.0 ** (excess_pressure / 2.0))


def calculate_completion_rate(workforce, productivity_effect):
    """
    Flow: How many projects are completed per month.

    This is determined by:
        - Number of workers (more people = more completions)
        - Their productivity (which varies with schedule pressure)

    Args:
        workforce: Number of employees
        productivity_effect: Multiplier on nominal productivity

    Returns:
        Projects completed per month
    """
    return workforce * NOMINAL_PRODUCTIVITY * productivity_effect


def calculate_quit_rate(workforce, quitting_effect):
    """
    Flow: How many employees leave per month.

    Combines:
        - Normal baseline attrition (people always leave for various reasons)
        - Pressure-induced quitting (burnout effect)

    Args:
        workforce: Number of employees
        quitting_effect: Multiplier on normal quit rate

    Returns:
        Employees leaving per month
    """
    monthly_normal_quit_fraction = NORMAL_QUIT_RATE_FRACTION / 12
    return workforce * monthly_normal_quit_fraction * quitting_effect


def calculate_hiring_rate(workforce, backlog):
    """
    Flow: How many employees are hired per month.

    This implements the BALANCING WORKLOAD LOOP:
    More backlog → hire more people → reduce pressure

    But there's a TIME DELAY: it takes TIME_TO_ADJUST_HIRING months
    to close the gap between actual and desired workforce.

    Args:
        workforce: Current number of employees
        backlog: Current project backlog

    Returns:
        New hires per month
    """
    # Calculate how many workers we THINK we need
    desired_workforce = backlog / PROJECTS_PER_DESIRED_EMPLOYEE

    # Calculate the gap
    workforce_gap = desired_workforce - workforce

    # Close the gap gradually over TIME_TO_ADJUST_HIRING months
    # If gap is positive, hire. If negative, stop hiring (but don't fire).
    hiring = max(0, workforce_gap / TIME_TO_ADJUST_HIRING)

    return hiring


# ========================================================================================
# PHASE 2: SIMULATION ENGINE - EULER INTEGRATION
# ========================================================================================

def run_simulation():
    """
    Execute the System Dynamics simulation using Euler integration.

    This is the core of SD: stepping through time, updating stocks based on flows.

    The order of operations in each time step is CRITICAL:
        1. Record current state (for plotting later)
        2. Calculate auxiliary variables (based on current stocks)
        3. Calculate all flows (based on auxiliary variables)
        4. Update stocks (based on flows)
        5. Advance time

    Returns:
        Dictionary containing time series of all key variables
    """
    # Initialize stocks (state variables)
    workforce = INITIAL_WORKFORCE
    project_backlog = INITIAL_BACKLOG

    # Initialize history tracking (for visualization)
    time_history = []
    workforce_history = []
    backlog_history = []
    pressure_history = []
    productivity_effect_history = []
    quit_rate_history = []
    hiring_rate_history = []
    completion_rate_history = []

    # Main simulation loop - step through time
    for t in range(SIMULATION_MONTHS + 1):
        # ================================================================================
        # STEP 1: RECORD CURRENT STATE
        # ================================================================================
        time_history.append(t)
        workforce_history.append(workforce)
        backlog_history.append(project_backlog)

        # ================================================================================
        # STEP 2: POLICY SHOCK - BIG CONTRACT ARRIVES
        # ================================================================================
        # At month 6, a large new contract arrives, suddenly increasing the backlog
        if t == TIME_SHOCK:
            project_backlog += SHOCK_SIZE
            print(f"\n{'='*70}")
            print(f"MONTH {t}: BIG CONTRACT SHOCK!")
            print(f"  +{SHOCK_SIZE} projects added to backlog")
            print(f"  New backlog: {project_backlog:.0f} projects")
            print(f"{'='*70}\n")

        # ================================================================================
        # STEP 3: CALCULATE AUXILIARY VARIABLES (based on current stock values)
        # ================================================================================
        schedule_pressure = calculate_schedule_pressure(project_backlog, workforce)
        productivity_effect = calculate_effect_of_pressure_on_productivity(schedule_pressure)
        quitting_effect = calculate_effect_of_pressure_on_quitting(schedule_pressure)

        # Record auxiliary variables
        pressure_history.append(schedule_pressure)
        productivity_effect_history.append(productivity_effect)

        # ================================================================================
        # STEP 4: CALCULATE FLOWS (rates of change)
        # ================================================================================
        completion_rate = calculate_completion_rate(workforce, productivity_effect)
        quit_rate = calculate_quit_rate(workforce, quitting_effect)
        hiring_rate = calculate_hiring_rate(workforce, project_backlog)

        # Record flow rates
        quit_rate_history.append(quit_rate)
        hiring_rate_history.append(hiring_rate)
        completion_rate_history.append(completion_rate)

        # ================================================================================
        # STEP 5: UPDATE STOCKS using Euler integration
        # ================================================================================
        # Stock equation: New_Value = Old_Value + (Inflows - Outflows) * DT

        # Workforce stock update
        # Inflow: hiring_rate, Outflow: quit_rate
        workforce += (hiring_rate - quit_rate) * DT
        workforce = max(1, workforce)  # Can't go below 1 employee (company still exists)

        # Project backlog stock update
        # Inflow: new_projects_rate, Outflow: completion_rate
        project_backlog += (NEW_PROJECTS_RATE - completion_rate) * DT
        project_backlog = max(0, project_backlog)  # Can't have negative backlog

        # ================================================================================
        # STEP 6: DIAGNOSTIC OUTPUT (every 6 months)
        # ================================================================================
        if t % 6 == 0:
            print(f"Month {t:2d}: Workforce={workforce:6.1f}, "
                  f"Backlog={project_backlog:6.1f}, "
                  f"Pressure={schedule_pressure:4.2f}, "
                  f"Productivity={productivity_effect:4.2f}, "
                  f"Hiring={hiring_rate:5.2f}, "
                  f"Quitting={quit_rate:4.2f}")

    # Return all histories for plotting
    return {
        'time': time_history,
        'workforce': workforce_history,
        'backlog': backlog_history,
        'pressure': pressure_history,
        'productivity_effect': productivity_effect_history,
        'quit_rate': quit_rate_history,
        'hiring_rate': hiring_rate_history,
        'completion_rate': completion_rate_history
    }


# ========================================================================================
# PHASE 3: VISUALIZATION AND ANALYSIS
# ========================================================================================

def plot_results(results):
    """
    Create comprehensive visualizations of the simulation results.

    The plots reveal the system's dynamic behavior, especially the
    OVERSHOOT ARCHETYPE caused by aggressive hiring in response to the shock.

    Args:
        results: Dictionary of time series data from run_simulation()
    """
    # Create a figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Workforce Dynamics: Overshoot Archetype from Aggressive Hiring Policy',
                 fontsize=16, fontweight='bold')

    time = results['time']

    # ================================================================================
    # PLOT 1: WORKFORCE AND BACKLOG (The Main Story)
    # ================================================================================
    ax1 = axes[0, 0]

    # Plot workforce (left y-axis)
    color = 'tab:blue'
    ax1.set_xlabel('Time (Months)', fontsize=11)
    ax1.set_ylabel('Workforce (Employees)', color=color, fontsize=11)
    ax1.plot(time, results['workforce'], color=color, linewidth=2, label='Workforce')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axvline(x=TIME_SHOCK, color='red', linestyle='--', alpha=0.5, label='Shock Event')
    ax1.grid(True, alpha=0.3)

    # Plot backlog (right y-axis)
    ax1_right = ax1.twinx()
    color = 'tab:orange'
    ax1_right.set_ylabel('Project Backlog', color=color, fontsize=11)
    ax1_right.plot(time, results['backlog'], color=color, linewidth=2, label='Backlog')
    ax1_right.tick_params(axis='y', labelcolor=color)

    ax1.set_title('Stock Behavior: Workforce Overshoot & Backlog Dynamics', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1_right.legend(loc='upper right')

    # ================================================================================
    # PLOT 2: SCHEDULE PRESSURE (The Key Driver)
    # ================================================================================
    ax2 = axes[0, 1]

    ax2.plot(time, results['pressure'], color='tab:red', linewidth=2, label='Schedule Pressure')
    ax2.axhline(y=NOMINAL_SCHEDULE_PRESSURE, color='green', linestyle='--',
                alpha=0.7, label=f'Nominal Pressure ({NOMINAL_SCHEDULE_PRESSURE})')
    ax2.axvline(x=TIME_SHOCK, color='red', linestyle='--', alpha=0.5, label='Shock Event')
    ax2.set_xlabel('Time (Months)', fontsize=11)
    ax2.set_ylabel('Schedule Pressure (Projects/Person)', fontsize=11)
    ax2.set_title('Schedule Pressure: The Core Feedback Driver', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # ================================================================================
    # PLOT 3: HIRING vs QUITTING (Flow Dynamics)
    # ================================================================================
    ax3 = axes[1, 0]

    ax3.plot(time, results['hiring_rate'], color='tab:green', linewidth=2, label='Hiring Rate')
    ax3.plot(time, results['quit_rate'], color='tab:red', linewidth=2, label='Quit Rate')
    ax3.axvline(x=TIME_SHOCK, color='red', linestyle='--', alpha=0.5, label='Shock Event')
    ax3.set_xlabel('Time (Months)', fontsize=11)
    ax3.set_ylabel('Flow Rate (Employees/Month)', fontsize=11)
    ax3.set_title('Workforce Flows: Hiring vs Attrition', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # ================================================================================
    # PLOT 4: PRODUCTIVITY EFFECT (Non-linear Impact)
    # ================================================================================
    ax4 = axes[1, 1]

    ax4.plot(time, results['productivity_effect'], color='tab:purple', linewidth=2,
             label='Productivity Effect')
    ax4.axhline(y=1.0, color='green', linestyle='--', alpha=0.7, label='Nominal (1.0)')
    ax4.axvline(x=TIME_SHOCK, color='red', linestyle='--', alpha=0.5, label='Shock Event')
    ax4.set_xlabel('Time (Months)', fontsize=11)
    ax4.set_ylabel('Productivity Multiplier', fontsize=11)
    ax4.set_title('Productivity: Non-linear Response to Pressure', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim([0, 1.3])

    plt.tight_layout()
    plt.savefig('workforce_dynamics_results.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ Plot saved as 'workforce_dynamics_results.png'")
    plt.show()


def print_analysis(results):
    """
    Print textual analysis of the simulation results.

    Helps users understand what they're seeing in the plots.
    """
    print("\n" + "="*70)
    print("SIMULATION ANALYSIS: THE OVERSHOOT ARCHETYPE")
    print("="*70)

    time = results['time']
    workforce = results['workforce']
    backlog = results['backlog']
    pressure = results['pressure']

    # Find peak workforce
    max_workforce_idx = workforce.index(max(workforce))
    max_workforce = workforce[max_workforce_idx]
    max_workforce_time = time[max_workforce_idx]

    # Find peak pressure
    max_pressure_idx = pressure.index(max(pressure))
    max_pressure = pressure[max_pressure_idx]
    max_pressure_time = time[max_pressure_idx]

    # Final values
    final_workforce = workforce[-1]
    final_backlog = backlog[-1]
    final_pressure = pressure[-1]

    print(f"\nINITIAL STATE (Month 0):")
    print(f"  Workforce: {INITIAL_WORKFORCE} employees")
    print(f"  Backlog: {INITIAL_BACKLOG} projects")
    print(f"  Pressure: {backlog[0]/workforce[0]:.2f} projects/person")

    print(f"\nSHOCK EVENT (Month {TIME_SHOCK}):")
    print(f"  +{SHOCK_SIZE} projects added")
    print(f"  New backlog: {backlog[TIME_SHOCK]:.0f} projects")

    print(f"\nSYSTEM RESPONSE - OVERSHOOT:")
    print(f"  Peak workforce: {max_workforce:.1f} employees (Month {max_workforce_time})")
    print(f"  Peak pressure: {max_pressure:.2f} projects/person (Month {max_pressure_time})")
    print(f"  → Aggressive hiring OVERSHOOTS the actual need")

    print(f"\nFINAL STATE (Month {SIMULATION_MONTHS}):")
    print(f"  Workforce: {final_workforce:.1f} employees")
    print(f"  Backlog: {final_backlog:.1f} projects")
    print(f"  Pressure: {final_pressure:.2f} projects/person")

    print(f"\nKEY INSIGHTS:")
    print(f"  1. AGGRESSIVE HIRING initially reduces backlog and pressure")
    print(f"  2. But HIGH PRESSURE degrades PRODUCTIVITY and increases TURNOVER")
    print(f"  3. This creates a REINFORCING SPIRAL: ")
    print(f"     High pressure → Low productivity → More backlog → Even higher pressure")
    print(f"  4. RESULT: The 'cure' (aggressive hiring) can make things worse!")
    print(f"  5. A more gradual, sustainable approach might work better")

    print("\n" + "="*70)
    print("This is a classic System Dynamics OVERSHOOT ARCHETYPE:")
    print("  - Quick fixes that ignore feedback loops")
    print("  - Can create worse long-term problems")
    print("  - Counter-intuitive behavior from time delays")
    print("="*70 + "\n")


# ========================================================================================
# PHASE 4: DIGITAL TWIN INTEGRATION POINTS
# ========================================================================================

DIGITAL_TWIN_INTEGRATION_GUIDE = """
================================================================================
DIGITAL TWIN INTEGRATION POINTS
================================================================================

This System Dynamics model represents STRATEGIC workforce planning for a
project-based company. Unlike the real-time twins in Labs 2-3, this is a
POLICY-LEVEL twin that operates on monthly/quarterly timescales.

DATA REQUIREMENTS FOR TWINNING:
--------------------------------

1. WORKFORCE (Stock)
   Real-World Data Source: Monthly Headcount Report
   Update Frequency: Monthly
   Data Provider: HR Information System (HRIS)
   Format: Total full-time employees
   Example: {"month": "2024-01", "workforce": 102}

2. PROJECT_BACKLOG (Stock)
   Real-World Data Source: Project Portfolio Dashboard
   Update Frequency: Monthly or Quarterly
   Data Provider: Project Management Office (PMO)
   Format: Number of active projects
   Example: {"quarter": "Q1-2024", "backlog": 487}

3. HIRING_RATE (Flow)
   Real-World Data Source: New Hire Report
   Update Frequency: Monthly
   Data Provider: HR Recruiting System
   Format: Number of employees hired in the period
   Example: {"month": "2024-01", "new_hires": 5}

4. QUIT_RATE (Flow)
   Real-World Data Source: Attrition Report
   Update Frequency: Monthly
   Data Provider: HR Information System
   Format: Number of voluntary departures
   Example: {"month": "2024-01", "attrition": 3}

5. COMPLETION_RATE (Flow)
   Real-World Data Source: Project Closure Report
   Update Frequency: Monthly or Quarterly
   Data Provider: Project Management System
   Format: Projects completed in period
   Example: {"month": "2024-01", "completed_projects": 45}

6. NEW_PROJECTS_RATE (Input)
   Real-World Data Source: Sales Pipeline / New Contract Data
   Update Frequency: Monthly
   Data Provider: Sales CRM or Contract Management System
   Format: New projects started in period
   Example: {"month": "2024-01", "new_projects": 18}

MODEL PARAMETERS (Calibrated from Historical Data):
----------------------------------------------------

7. NOMINAL_PRODUCTIVITY
   Calibration Source: Historical project completion data
   Calculation: Total projects completed / Total person-months
   Example: 2,400 projects / 480 person-months = 5.0 projects/person/month

8. NORMAL_QUIT_RATE_FRACTION
   Calibration Source: Multi-year HR attrition data
   Calculation: Average annual turnover rate
   Example: Average 5% annual turnover in stable periods

9. Effect Functions (Productivity & Quitting curves)
   Calibration Source: Historical correlation analysis
   Method: Plot historical pressure vs. productivity/turnover
   Refinement: Expert judgment from HR and PMO leaders

DIGITAL TWIN OPERATIONAL MODES:
--------------------------------

MODE 1: MONITORING (Passive Twin)
  - Continuously update stocks with real data
  - Compare actual vs. simulated flows
  - Alert when divergence indicates model drift or real-world change

MODE 2: PREDICTION (Forecast Twin)
  - Run model forward from current state
  - Predict workforce needs 6-12 months ahead
  - Identify potential pressure buildup

MODE 3: POLICY TESTING (What-If Twin)
  - Test hiring policies before implementation
  - Example: "What if we hire 10 people/month for 3 months?"
  - Reveal unintended consequences (like this lab showed!)

MODE 4: OPTIMIZATION (Prescriptive Twin)
  - Search for optimal hiring rate trajectories
  - Balance multiple objectives (backlog, pressure, cost)
  - Recommend data-driven policies

INTEGRATION ARCHITECTURE:
-------------------------

┌─────────────────────────────────────────────────────────────┐
│  REAL COMPANY SYSTEMS                                       │
├─────────────────────────────────────────────────────────────┤
│  HRIS  │  PMO System  │  Sales CRM  │  Finance ERP         │
└────┬──────────┬──────────────┬──────────────┬──────────────┘
     │          │              │              │
     └──────────┴──────────────┴──────────────┘
                       │
           ┌───────────▼───────────┐
           │   DATA INTEGRATION    │
           │   ETL / API Layer     │
           └───────────┬───────────┘
                       │
           ┌───────────▼───────────┐
           │  DIGITAL TWIN ENGINE  │
           │  (This SD Model)      │
           └───────────┬───────────┘
                       │
           ┌───────────▼───────────┐
           │  DASHBOARD / ALERTS   │
           │  (Visualization)      │
           └───────────────────────┘

EXAMPLE API INTEGRATION CODE:
------------------------------

```python
import requests
from workforce_dynamics_model import run_simulation

# Fetch current state from company systems
def get_current_state():
    # Get workforce from HRIS
    workforce_data = requests.get('https://hris.company.com/api/headcount').json()
    current_workforce = workforce_data['total_employees']

    # Get backlog from PMO
    pmo_data = requests.get('https://pmo.company.com/api/active_projects').json()
    current_backlog = pmo_data['active_count']

    return current_workforce, current_backlog

# Initialize model with real data
INITIAL_WORKFORCE, INITIAL_BACKLOG = get_current_state()

# Run prediction
results = run_simulation()

# Alert if pressure will exceed threshold
if max(results['pressure']) > 8.0:
    send_alert("Warning: Model predicts high schedule pressure in 3 months")
```

CALIBRATION WORKFLOW:
---------------------

1. COLLECT HISTORICAL DATA (2-3 years minimum)
   - Monthly workforce levels
   - Monthly project backlog
   - Monthly hiring and attrition
   - Monthly project completions

2. FIT MODEL PARAMETERS
   - Adjust NOMINAL_PRODUCTIVITY to match average completion rate
   - Adjust quit rate to match average attrition
   - Tune effect functions using regression/optimization

3. VALIDATE MODEL
   - Run simulation on historical period
   - Compare simulated vs. actual trajectories
   - Calculate error metrics (RMSE, MAPE)

4. ITERATIVE REFINEMENT
   - Identify periods of large deviation
   - Investigate root causes (model structure or data quality)
   - Add complexity only if needed (parsimony principle)

SUCCESS METRICS FOR DIGITAL TWIN:
----------------------------------

- Prediction Accuracy: MAPE < 15% for 3-month workforce forecast
- Early Warning: Detect pressure buildups 2+ months before HR sees it
- Policy Value: Prevent at least one "overshoot" scenario per year
- User Adoption: Used by leadership in quarterly planning meetings

================================================================================
END OF DIGITAL TWIN INTEGRATION GUIDE
================================================================================
"""


# ========================================================================================
# MAIN EXECUTION
# ========================================================================================

def main():
    """
    Main execution function for the workforce dynamics simulation.
    """
    print("\n")
    print("╔" + "═"*76 + "╗")
    print("║" + " "*76 + "║")
    print("║" + "  LAB 4: WORKFORCE DYNAMICS - SYSTEM DYNAMICS MODEL".center(76) + "║")
    print("║" + "  Demonstrating Stocks, Flows, and the Overshoot Archetype".center(76) + "║")
    print("║" + " "*76 + "║")
    print("╚" + "═"*76 + "╝")

    print("\nSIMULATION CONFIGURATION:")
    print(f"  Duration: {SIMULATION_MONTHS} months")
    print(f"  Time step: {DT} month")
    print(f"  Initial workforce: {INITIAL_WORKFORCE} employees")
    print(f"  Initial backlog: {INITIAL_BACKLOG} projects")
    print(f"  Shock event: Month {TIME_SHOCK} (+{SHOCK_SIZE} projects)")

    print("\nRunning simulation...")
    print("-" * 70)

    # Run the simulation
    results = run_simulation()

    print("-" * 70)
    print("Simulation complete!")

    # Analyze results
    print_analysis(results)

    # Create visualizations
    print("\nGenerating visualizations...")
    plot_results(results)

    # Print Digital Twin integration information
    print(DIGITAL_TWIN_INTEGRATION_GUIDE)

    print("\n" + "="*70)
    print("EXPERIMENT IDEAS:")
    print("="*70)
    print("Try modifying these parameters and re-running:")
    print("  1. TIME_TO_ADJUST_HIRING = 6  (slower hiring response)")
    print("  2. SHOCK_SIZE = 200  (smaller shock)")
    print("  3. NEW_PROJECTS_RATE = 25  (higher steady-state inflow)")
    print("  4. Modify effect functions (make productivity less sensitive)")
    print("\nObserve how system behavior changes!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
