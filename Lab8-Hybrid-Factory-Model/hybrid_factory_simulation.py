"""
Lab 8: Hybrid Factory Model - Integrating DES, ABM, and SD
===========================================================

A hybrid simulation that demonstrates the integration of three modeling paradigms:
- Discrete Event Simulation (DES): Production process flow
- Agent-Based Modeling (ABM): Autonomous maintenance technicians
- System Dynamics (SD): Continuous machine health degradation

This model shows how events in one paradigm trigger actions in another,
creating a realistic factory simulation where machine failures interrupt
production and require technician intervention.

Prerequisites:
    - simpy (DES framework)
    - mesa (ABM framework)
    - numpy
    - matplotlib

Usage:
    python hybrid_factory_simulation.py
"""

import simpy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from collections import deque
from enum import Enum
import random


# ========================================================================================
# CONFIGURATION
# ========================================================================================

# Simulation parameters
SIM_TIME = 480  # minutes (8 hours)
RANDOM_SEED = 42

# Production parameters (DES)
PART_ARRIVAL_MEAN = 5.0  # minutes between part arrivals
PART_ARRIVAL_STD = 2.0
MACHINE_PROCESS_TIME = (2.0, 4.0)  # (min, max) uniform distribution

# Machine health parameters (SD)
INITIAL_HEALTH = 100.0
HEALTH_THRESHOLD = 20.0  # Below this, machine breaks
DEGRADATION_RATE_BUSY = 0.15  # Health loss per minute when machine is busy
DEGRADATION_RATE_IDLE = 0.02  # Health loss per minute when machine is idle

# Repair parameters (ABM)
NUM_TECHNICIANS = 2
REPAIR_TIME_MEAN = 15.0  # minutes
REPAIR_TIME_STD = 5.0
REPAIR_RATE = 10.0  # Health gain per minute during repair


# ========================================================================================
# TECHNICIAN AGENT STATES
# ========================================================================================

class TechnicianState(Enum):
    """States for the technician agent's statechart."""
    IDLE = "Idle"
    MOVING_TO_MACHINE = "MovingToMachine"
    REPAIRING = "Repairing"


# ========================================================================================
# PART ENTITY (DES)
# ========================================================================================

class Part:
    """
    A simple entity representing a part in the production process.

    In DES, entities flow through the process. This is analogous to
    the custom agent type in AnyLogic's Process Modeling Library.
    """

    part_counter = 0  # Class variable for unique IDs

    def __init__(self, arrival_time):
        """
        Initialize a part.

        Args:
            arrival_time: Simulation time when part was created
        """
        Part.part_counter += 1
        self.id = Part.part_counter
        self.arrival_time = arrival_time
        self.service_start_time = None
        self.completion_time = None

    def __repr__(self):
        return f"Part({self.id})"


# ========================================================================================
# TECHNICIAN AGENT (ABM)
# ========================================================================================

class TechnicianAgent:
    """
    Technician agent with statechart behavior.

    States: Idle -> MovingToMachine -> Repairing -> Idle

    The technician responds to repair requests and travels to the machine
    to perform maintenance, restoring the machine's health.

    This implements ABM principles (autonomous agents with state-based behavior)
    without requiring the full Mesa framework infrastructure.
    """

    def __init__(self, model, technician_id):
        """
        Initialize technician agent.

        Args:
            model: The FactoryModel instance
            technician_id: Unique identifier for this technician
        """
        self.model = model
        self.technician_id = technician_id
        self.state = TechnicianState.IDLE
        self.repair_start_time = None
        self.repair_duration = None

        # Position (for visualization)
        self.x = 10 + technician_id * 30  # Spread out in waiting area
        self.y = 10

    def request_repair(self):
        """
        Called when the factory needs this technician to repair the machine.

        Transition: Idle -> MovingToMachine
        """
        if self.state == TechnicianState.IDLE:
            self.state = TechnicianState.MOVING_TO_MACHINE
            # In a spatial model, we'd move the agent. Here, we instantaneously arrive.
            # Transition to Repairing state
            self.arrive_at_machine()

    def arrive_at_machine(self):
        """
        Called when technician arrives at the machine.

        Transition: MovingToMachine -> Repairing
        """
        self.state = TechnicianState.REPAIRING
        self.repair_start_time = self.model.env.now
        # Sample repair duration
        self.repair_duration = max(1.0, random.gauss(REPAIR_TIME_MEAN, REPAIR_TIME_STD))

        # Log
        print(f"  [ABM] Technician {self.technician_id} started repairing at t={self.model.env.now:.1f}")

        # Update position (for visualization)
        self.x = 200  # Machine location
        self.y = 100

    def step(self):
        """
        Called every simulation step (Mesa convention).

        Checks if repair is complete and transitions back to Idle.
        """
        if self.state == TechnicianState.REPAIRING:
            elapsed_time = self.model.env.now - self.repair_start_time

            if elapsed_time >= self.repair_duration:
                # Repair complete!
                self.finish_repair()

    def finish_repair(self):
        """
        Called when repair is finished.

        Transition: Repairing -> Idle
        """
        # Restore machine health (ABM -> SD interaction)
        self.model.machine_health = INITIAL_HEALTH

        # Unblock the machine (ABM -> DES interaction)
        self.model.machine_is_broken = False

        # Log
        print(f"  [ABM] Technician {self.technician_id} finished repair at t={self.model.env.now:.1f}")
        print(f"  [DES] Machine unblocked and back in service")

        # Return to idle state
        self.state = TechnicianState.IDLE

        # Return to waiting area (for visualization)
        self.x = 10 + self.technician_id * 30
        self.y = 10


# ========================================================================================
# HYBRID FACTORY MODEL
# ========================================================================================

class FactoryModel:
    """
    Main hybrid factory model integrating DES, ABM, and SD.

    This class orchestrates:
    - DES: SimPy processes for part production
    - ABM: Mesa technician agents
    - SD: Continuous machine health equations
    - Integration: Cross-paradigm event triggering
    """

    def __init__(self, seed=RANDOM_SEED):
        """
        Initialize the factory model.

        Args:
            seed: Random seed for reproducibility
        """
        # Random seed
        random.seed(seed)
        np.random.seed(seed)

        # ===== DES Components (SimPy) =====
        self.env = simpy.Environment()

        # Machine resource (capacity = 1)
        self.machine = simpy.Resource(self.env, capacity=1)

        # Queue for parts waiting for machine
        self.queue = []

        # Statistics
        self.parts_created = 0
        self.parts_completed = 0
        self.total_wait_time = 0.0
        self.total_service_time = 0.0

        # ===== SD Components =====
        self.machine_health = INITIAL_HEALTH
        self.machine_is_broken = False

        # ===== ABM Components (Mesa) =====
        # Note: We don't use Mesa's schedule here because SimPy controls time
        # We manually step the agents when needed
        self.technicians = [TechnicianAgent(self, i) for i in range(NUM_TECHNICIANS)]

        # ===== Data Collection =====
        self.time_series = {
            'time': [],
            'queue_length': [],
            'machine_health': [],
            'machine_busy': [],
            'machine_broken': [],
            'parts_completed': [],
            'technicians_idle': [],
            'technicians_repairing': [],
        }

    def record_state(self):
        """Record current state for visualization."""
        self.time_series['time'].append(self.env.now)
        self.time_series['queue_length'].append(len(self.queue))
        self.time_series['machine_health'].append(self.machine_health)
        self.time_series['machine_busy'].append(len(self.machine.users))
        self.time_series['machine_broken'].append(int(self.machine_is_broken))
        self.time_series['parts_completed'].append(self.parts_completed)

        # Count technician states
        idle_count = sum(1 for t in self.technicians if t.state == TechnicianState.IDLE)
        repair_count = sum(1 for t in self.technicians if t.state == TechnicianState.REPAIRING)
        self.time_series['technicians_idle'].append(idle_count)
        self.time_series['technicians_repairing'].append(repair_count)

    def update_machine_health(self, dt):
        """
        Update machine health using SD equations.

        Args:
            dt: Time step (minutes)
        """
        # Determine degradation rate based on machine state
        if len(self.machine.users) > 0:  # Machine is busy
            degradation = DEGRADATION_RATE_BUSY * dt
        else:  # Machine is idle
            degradation = DEGRADATION_RATE_IDLE * dt

        # Determine repair rate (positive contribution from technicians)
        repair = 0.0
        for tech in self.technicians:
            if tech.state == TechnicianState.REPAIRING:
                repair += REPAIR_RATE * dt

        # Update health (stock equation)
        self.machine_health += repair - degradation

        # Bounds checking
        self.machine_health = max(0.0, min(INITIAL_HEALTH, self.machine_health))

    def check_health_threshold(self):
        """
        Check if machine health has dropped below threshold.

        SD -> DES -> ABM interaction:
        - SD: Health drops below threshold
        - DES: Block the machine
        - ABM: Dispatch a technician
        """
        if self.machine_health <= HEALTH_THRESHOLD and not self.machine_is_broken:
            # Machine breaks!
            self.machine_is_broken = True
            print(f"\n[SD] Machine health critical! ({self.machine_health:.1f}) at t={self.env.now:.1f}")
            print(f"[DES] Machine blocked - production halted")

            # Find an idle technician (ABM)
            for tech in self.technicians:
                if tech.state == TechnicianState.IDLE:
                    print(f"[ABM] Dispatching Technician {tech.technician_id} to repair")
                    tech.request_repair()
                    break

    def part_source(self):
        """
        DES process: Generate parts arriving to the system.

        This is the 'Source' block in Process Modeling.
        """
        while True:
            # Create a new part
            part = Part(self.env.now)
            self.parts_created += 1
            self.queue.append(part)

            print(f"[DES] {part} arrived at t={self.env.now:.1f} (Queue: {len(self.queue)})")

            # Trigger the machine process to check if it can service parts
            self.env.process(self.machine_service(part))

            # Wait for next arrival
            interarrival = max(0.1, random.gauss(PART_ARRIVAL_MEAN, PART_ARRIVAL_STD))
            yield self.env.timeout(interarrival)

    def machine_service(self, part):
        """
        DES process: Machine services a part.

        This represents the 'Service' block with seize-delay-release logic.

        Args:
            part: The Part entity to process
        """
        # Wait in queue if machine is broken or busy
        while self.machine_is_broken or len(self.machine.queue) >= self.machine.capacity:
            yield self.env.timeout(0.5)  # Check every 30 seconds

        # Request machine resource (seize)
        with self.machine.request() as request:
            yield request

            # Remove from queue
            if part in self.queue:
                self.queue.remove(part)

            # Record wait time
            part.service_start_time = self.env.now
            wait_time = part.service_start_time - part.arrival_time
            self.total_wait_time += wait_time

            # Process the part (delay)
            service_time = random.uniform(*MACHINE_PROCESS_TIME)
            print(f"[DES] {part} service started at t={self.env.now:.1f} (duration: {service_time:.1f} min)")

            # Service in chunks to allow health checks
            elapsed = 0.0
            chunk = 0.5  # Check every 30 seconds
            while elapsed < service_time:
                if self.machine_is_broken:
                    # Service interrupted by breakdown!
                    print(f"[DES] {part} service interrupted at t={self.env.now:.1f}!")
                    self.queue.insert(0, part)  # Return to front of queue
                    yield self.env.timeout(1.0)  # Wait for repair
                    continue

                wait_time = min(chunk, service_time - elapsed)
                yield self.env.timeout(wait_time)
                elapsed += wait_time

            # Service complete (release happens automatically via 'with')
            part.completion_time = self.env.now
            self.total_service_time += service_time
            self.parts_completed += 1

            print(f"[DES] {part} completed at t={self.env.now:.1f} (Total: {self.parts_completed})")

    def monitor_process(self):
        """
        Background process to update SD model and ABM agents.

        This integrates the continuous SD updates with discrete SimPy events.
        """
        dt = 0.5  # Time step for SD integration (minutes)

        while True:
            # Update machine health (SD)
            self.update_machine_health(dt)

            # Check health threshold (SD -> DES -> ABM)
            self.check_health_threshold()

            # Step ABM agents
            for tech in self.technicians:
                tech.step()

            # Record data
            self.record_state()

            # Wait for next time step
            yield self.env.timeout(dt)

    def run(self, until=SIM_TIME):
        """
        Run the hybrid simulation.

        Args:
            until: Simulation duration (minutes)
        """
        print("="*70)
        print("HYBRID FACTORY SIMULATION")
        print("="*70)
        print(f"Simulation time: {until} minutes")
        print(f"Number of technicians: {NUM_TECHNICIANS}")
        print(f"Health threshold: {HEALTH_THRESHOLD}")
        print("="*70)
        print()

        # Start processes
        self.env.process(self.part_source())
        self.env.process(self.monitor_process())

        # Run simulation
        self.env.run(until=until)

        # Print statistics
        self.print_statistics()

    def print_statistics(self):
        """Print simulation statistics."""
        print("\n" + "="*70)
        print("SIMULATION STATISTICS")
        print("="*70)
        print(f"Parts created:    {self.parts_created}")
        print(f"Parts completed:  {self.parts_completed}")
        print(f"Parts in queue:   {len(self.queue)}")

        if self.parts_completed > 0:
            avg_wait = self.total_wait_time / self.parts_completed
            avg_service = self.total_service_time / self.parts_completed
            print(f"\nAverage wait time:    {avg_wait:.2f} minutes")
            print(f"Average service time: {avg_service:.2f} minutes")
            print(f"Average total time:   {avg_wait + avg_service:.2f} minutes")

        # Count breakdowns
        breakdown_times = []
        was_broken = False
        breakdown_start = 0

        for i, (time, broken) in enumerate(zip(self.time_series['time'],
                                                 self.time_series['machine_broken'])):
            if broken and not was_broken:
                breakdown_start = time
                was_broken = True
            elif not broken and was_broken:
                breakdown_times.append(time - breakdown_start)
                was_broken = False

        print(f"\nMachine breakdowns:   {len(breakdown_times)}")
        if len(breakdown_times) > 0:
            print(f"Average downtime:     {np.mean(breakdown_times):.2f} minutes")
            print(f"Total downtime:       {np.sum(breakdown_times):.2f} minutes")
            print(f"Availability:         {(1 - np.sum(breakdown_times)/SIM_TIME)*100:.1f}%")

        print("="*70)


# ========================================================================================
# VISUALIZATION
# ========================================================================================

def plot_results(model):
    """
    Create comprehensive visualization of the hybrid simulation.

    Shows data from all three paradigms: DES, ABM, and SD.

    Args:
        model: The FactoryModel instance with recorded data
    """
    fig = plt.figure(figsize=(14, 10))

    # Extract time series
    time = np.array(model.time_series['time'])
    queue_length = np.array(model.time_series['queue_length'])
    machine_health = np.array(model.time_series['machine_health'])
    machine_busy = np.array(model.time_series['machine_busy'])
    machine_broken = np.array(model.time_series['machine_broken'])
    parts_completed = np.array(model.time_series['parts_completed'])
    techs_idle = np.array(model.time_series['technicians_idle'])
    techs_repairing = np.array(model.time_series['technicians_repairing'])

    # ===== Plot 1: Machine Health (SD) =====
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(time, machine_health, 'b-', linewidth=2, label='Machine Health')
    ax1.axhline(y=HEALTH_THRESHOLD, color='r', linestyle='--', label='Critical Threshold')
    ax1.fill_between(time, 0, HEALTH_THRESHOLD, alpha=0.2, color='red')
    ax1.set_xlabel('Time (minutes)')
    ax1.set_ylabel('Health')
    ax1.set_title('System Dynamics: Machine Health Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # ===== Plot 2: Machine State (DES) =====
    ax2 = plt.subplot(3, 2, 2)
    # Create stacked area showing machine state
    ax2.fill_between(time, 0, machine_busy, alpha=0.6, color='green', label='Busy (Processing)')
    ax2.fill_between(time, 0, machine_broken, alpha=0.6, color='red', label='Broken (Down)')
    ax2.set_xlabel('Time (minutes)')
    ax2.set_ylabel('State')
    ax2.set_title('DES: Machine State')
    ax2.set_ylim([0, 1.2])
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # ===== Plot 3: Queue Length (DES) =====
    ax3 = plt.subplot(3, 2, 3)
    ax3.plot(time, queue_length, 'orange', linewidth=2)
    ax3.fill_between(time, 0, queue_length, alpha=0.3, color='orange')
    ax3.set_xlabel('Time (minutes)')
    ax3.set_ylabel('Parts Waiting')
    ax3.set_title('DES: Queue Length (Parts Waiting for Machine)')
    ax3.grid(True, alpha=0.3)

    # ===== Plot 4: Cumulative Production (DES) =====
    ax4 = plt.subplot(3, 2, 4)
    ax4.plot(time, parts_completed, 'g-', linewidth=2)
    ax4.set_xlabel('Time (minutes)')
    ax4.set_ylabel('Parts Completed')
    ax4.set_title('DES: Cumulative Production')
    ax4.grid(True, alpha=0.3)

    # ===== Plot 5: Technician States (ABM) =====
    ax5 = plt.subplot(3, 2, 5)
    ax5.plot(time, techs_idle, 'b-', linewidth=2, label='Idle', marker='o', markersize=2)
    ax5.plot(time, techs_repairing, 'r-', linewidth=2, label='Repairing', marker='s', markersize=2)
    ax5.set_xlabel('Time (minutes)')
    ax5.set_ylabel('Number of Technicians')
    ax5.set_title('ABM: Technician States Over Time')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # ===== Plot 6: Integrated View =====
    ax6 = plt.subplot(3, 2, 6)
    # Normalize values for comparison
    norm_health = machine_health / 100
    norm_queue = queue_length / (max(queue_length) + 1)
    norm_production = parts_completed / (max(parts_completed) + 1)

    ax6.plot(time, norm_health, 'b-', linewidth=2, label='Health (normalized)', alpha=0.7)
    ax6.plot(time, norm_queue, 'orange', linewidth=2, label='Queue (normalized)', alpha=0.7)
    ax6.plot(time, norm_production, 'g-', linewidth=2, label='Production (normalized)', alpha=0.7)

    # Shade breakdown periods
    for i in range(len(time)):
        if machine_broken[i]:
            ax6.axvspan(time[i], time[min(i+1, len(time)-1)], alpha=0.2, color='red')

    ax6.set_xlabel('Time (minutes)')
    ax6.set_ylabel('Normalized Values')
    ax6.set_title('Integrated Hybrid View: SD + DES + ABM')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    plt.suptitle('Hybrid Factory Simulation: DES + ABM + SD Integration',
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()

    return fig


# ========================================================================================
# MAIN EXECUTION
# ========================================================================================

def main():
    """
    Main function: Run simulation and display results.
    """
    # Create and run model
    model = FactoryModel(seed=RANDOM_SEED)
    model.run(until=SIM_TIME)

    # Visualize results
    fig = plot_results(model)

    # Save figure
    output_file = 'hybrid_factory_results.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Visualization saved to {output_file}")

    # Show plot
    plt.show()


if __name__ == "__main__":
    main()
