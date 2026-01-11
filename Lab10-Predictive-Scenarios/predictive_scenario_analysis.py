"""
Lab 10: Predictive 'What-If' Scenario Analysis
===============================================

Demonstrates the full predictive analysis workflow for a Digital Twin:
1. Run a "base twin" in real-time mode to establish operational state
2. At a decision point, save the simulation state ("fork the timeline")
3. Launch multiple faster-than-real-time (FTRT) simulations with different scenarios
4. Compare KPIs to make data-driven decisions

This shows how Digital Twins enable "looking into the future" to evaluate
alternative strategies before committing to real-world actions.

Prerequisites:
    - simpy (discrete event simulation)

Usage:
    python predictive_scenario_analysis.py

What to observe:
    - Real-time twin runs for 10 seconds
    - At t=10s, state is saved and analysis triggered
    - Two FTRT clones run instantly to simulate 8-hour futures
    - KPIs compared: which shift schedule produces more parts?
"""

import simpy
import random
import copy
from datetime import datetime


# ========================================================================================
# SIMULATION PARAMETERS
# ========================================================================================

# Production parameters
PART_ARRIVAL_INTERVAL = 3.0  # minutes between part arrivals
MACHINE_PROCESS_TIME = (2.0, 4.0)  # (min, max) processing time range

# Reliability parameters
MACHINE_MTBF = 60.0  # Mean Time Between Failures (minutes)
MACHINE_REPAIR_TIME = (10.0, 20.0)  # (min, max) repair duration

# Shift schedules (technician availability over time)
# Format: {simulation_time_minutes: number_of_technicians}
SCENARIO_BASELINE = {
    0: 1,  # 1 technician for entire shift
}

SCENARIO_PROPOSED = {
    0: 1,      # Start with 1 technician
    120: 2,    # Add 2nd technician at 2 hours (busy period)
    360: 1,    # Back to 1 technician at 6 hours
}

# Real-time simulation parameters
REALTIME_FACTOR = 0.5  # 1 sim minute = 0.5 real seconds (2x speed)
DECISION_POINT = 10.0  # Real seconds before triggering analysis


# ========================================================================================
# FACTORY SIMULATION MODEL
# ========================================================================================

class Factory:
    """
    Factory simulation model with machine failures and maintenance crew.

    This model demonstrates:
    - DES: Part arrivals and processing
    - Resource contention: Shared maintenance technicians
    - Stochastic failures: Machine breakdowns
    - State management: Save/load capability for forking
    """

    def __init__(self, env, shift_schedule, verbose=True):
        """
        Initialize factory model.

        Args:
            env: SimPy environment (real-time or standard)
            shift_schedule: Dict of {time: technician_count}
            verbose: Print detailed logs
        """
        self.env = env
        self.shift_schedule = shift_schedule
        self.verbose = verbose

        # Resources
        self.machine_queue = simpy.Store(env)

        # Initialize technician resource with capacity from schedule
        initial_tech_count = shift_schedule[0]
        self.technicians = simpy.Resource(env, capacity=initial_tech_count)

        # Machine state
        self.machine_state = "idle"  # "idle", "processing", "broken"
        self.time_to_next_failure = self._sample_mtbf()
        self.current_part_remaining_time = 0.0
        self.current_repair_remaining_time = 0.0

        # Statistics (KPIs)
        self.parts_created = 0
        self.parts_produced = 0
        self.total_downtime = 0.0
        self.downtime_start = None

        # Process tracking
        self.processes = []

    def _sample_mtbf(self):
        """Sample time until next failure from exponential distribution."""
        return random.expovariate(1.0 / MACHINE_MTBF)

    def _sample_process_time(self):
        """Sample part processing time."""
        return random.uniform(*MACHINE_PROCESS_TIME)

    def _sample_repair_time(self):
        """Sample machine repair time."""
        return random.uniform(*MACHINE_REPAIR_TIME)

    def _log(self, message):
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[t={self.env.now:6.1f}] {message}")

    # ================================================================================
    # CORE SIMULATION PROCESSES
    # ================================================================================

    def part_generator(self):
        """
        Generate parts arriving to the factory.

        Parts enter the queue and wait for machine processing.
        """
        while True:
            # Create new part
            self.parts_created += 1
            part_id = self.parts_created

            self._log(f"Part {part_id} arrived")

            # Put part in queue
            yield self.machine_queue.put(part_id)

            # Wait for next arrival
            yield self.env.timeout(PART_ARRIVAL_INTERVAL)

    def machine_process(self):
        """
        Main machine process: process parts and handle failures.

        This is the heart of the simulation, managing:
        - Part processing
        - Machine health tracking
        - Failure triggering
        """
        while True:
            # Wait for a part to arrive
            part_id = yield self.machine_queue.get()

            # Start processing
            self.machine_state = "processing"
            process_time = self._sample_process_time()
            self.current_part_remaining_time = process_time

            self._log(f"Machine started processing Part {part_id} (duration: {process_time:.1f} min)")

            # Process in small chunks to check for failures
            while self.current_part_remaining_time > 0:
                # Determine next event: part completion or failure
                time_to_complete = self.current_part_remaining_time
                time_to_failure = self.time_to_next_failure

                if time_to_failure < time_to_complete:
                    # Machine will fail before part completes!
                    yield self.env.timeout(time_to_failure)

                    # Update remaining time
                    self.current_part_remaining_time -= time_to_failure
                    self.time_to_next_failure = 0

                    # Machine breaks
                    self._log(f"⚠ Machine FAILED during Part {part_id} processing!")
                    self._log(f"   Remaining work on part: {self.current_part_remaining_time:.1f} min")

                    # Trigger repair
                    yield self.env.process(self.repair_machine())

                    # After repair, continue processing same part
                    self._log(f"Machine resuming Part {part_id} processing")

                else:
                    # Part completes before failure
                    yield self.env.timeout(time_to_complete)

                    # Update machine health
                    self.time_to_next_failure -= time_to_complete
                    self.current_part_remaining_time = 0

            # Part completed
            self.parts_produced += 1
            self.machine_state = "idle"

            self._log(f"Part {part_id} completed (Total: {self.parts_produced})")

    def repair_machine(self):
        """
        Repair process: request technician and perform maintenance.

        This demonstrates resource contention - multiple machines (if we had them)
        would compete for limited technicians.
        """
        # Machine is now broken
        self.machine_state = "broken"
        self.downtime_start = self.env.now

        # Request technician from resource pool
        self._log(f"Requesting technician for repair...")

        with self.technicians.request() as req:
            # Wait for technician to become available
            yield req

            # Technician arrived
            repair_time = self._sample_repair_time()
            self.current_repair_remaining_time = repair_time

            self._log(f"✓ Technician assigned. Repair duration: {repair_time:.1f} min")

            # Perform repair
            yield self.env.timeout(repair_time)

            # Repair complete
            self.current_repair_remaining_time = 0
            downtime_duration = self.env.now - self.downtime_start
            self.total_downtime += downtime_duration

            # Machine is functional again
            self.time_to_next_failure = self._sample_mtbf()
            self.machine_state = "idle"

            self._log(f"✓ Repair completed. Downtime: {downtime_duration:.1f} min")

    def shift_manager(self):
        """
        Manage technician availability based on shift schedule.

        This process changes the resource capacity at specified times,
        implementing different scenarios (e.g., adding technicians during busy periods).
        """
        # Sort schedule by time
        schedule_times = sorted(self.shift_schedule.keys())

        for i, time in enumerate(schedule_times):
            if time == 0:
                continue  # Initial capacity already set

            # Wait until schedule change time
            yield self.env.timeout(time - self.env.now)

            # Change technician capacity
            new_capacity = self.shift_schedule[time]
            old_capacity = self.technicians.capacity
            self.technicians._capacity = new_capacity  # Update capacity

            self._log(f"📋 Shift change: Technicians {old_capacity} → {new_capacity}")

    # ================================================================================
    # STATE MANAGEMENT (FOR FORKING)
    # ================================================================================

    def save_state(self):
        """
        Save high-level simulation state for forking.

        This captures the essential state needed to resume simulation
        from this point with different scenarios.

        Returns:
            dict: State snapshot
        """
        state = {
            "simulation_time": self.env.now,
            "parts_in_queue": len(self.machine_queue.items),
            "machine_state": self.machine_state,
            "time_to_next_failure": self.time_to_next_failure,
            "current_part_remaining_time": self.current_part_remaining_time,
            "current_repair_remaining_time": self.current_repair_remaining_time,
            "technicians_available": self.technicians.capacity,
            "parts_created": self.parts_created,
            "parts_produced": self.parts_produced,
            "total_downtime": self.total_downtime,
        }

        return state

    def run(self, initial_state=None, duration=None):
        """
        Start factory simulation with optional initial state.

        Args:
            initial_state: Dict from save_state() to resume from
            duration: Simulation duration (if None, runs indefinitely)
        """
        if initial_state is not None:
            # LOAD STATE: Initialize from saved snapshot
            self._log("Loading initial state from snapshot...")

            # Restore statistics
            self.parts_created = initial_state["parts_created"]
            self.parts_produced = initial_state["parts_produced"]
            self.total_downtime = initial_state["total_downtime"]

            # Restore machine state
            self.machine_state = initial_state["machine_state"]
            self.time_to_next_failure = initial_state["time_to_next_failure"]
            self.current_part_remaining_time = initial_state["current_part_remaining_time"]
            self.current_repair_remaining_time = initial_state["current_repair_remaining_time"]

            # Restore queue (pre-populate with dummy parts)
            for _ in range(initial_state["parts_in_queue"]):
                self.machine_queue.put(self.parts_created + 1)  # Dummy part IDs

            self._log(f"State loaded: {initial_state['parts_in_queue']} parts in queue, "
                     f"machine {initial_state['machine_state']}")

        # Start processes
        self.processes.append(self.env.process(self.part_generator()))
        self.processes.append(self.env.process(self.machine_process()))
        self.processes.append(self.env.process(self.shift_manager()))

        # Run simulation
        if duration is not None:
            self.env.run(until=self.env.now + duration)


# ========================================================================================
# PREDICTIVE CLONE RUNNER
# ========================================================================================

def run_predictive_clone(initial_state, scenario_schedule, duration=480):
    """
    Run a faster-than-real-time (FTRT) clone simulation from saved state.

    This is the "forked timeline" that explores a future scenario.

    Args:
        initial_state: State snapshot from base twin
        scenario_schedule: Shift schedule for this scenario
        duration: Simulation duration (minutes)

    Returns:
        dict: KPIs from this scenario
    """
    print(f"\n{'='*70}")
    print(f"Running FTRT Clone: {duration} minute simulation")
    print(f"Shift schedule: {scenario_schedule}")
    print(f"{'='*70}")

    # Create standard (non-realtime) environment for speed
    clone_env = simpy.Environment(initial_time=initial_state["simulation_time"])

    # Create factory clone with scenario
    clone_factory = Factory(clone_env, scenario_schedule, verbose=False)

    # Initialize from saved state
    clone_factory.run(initial_state=initial_state, duration=duration)

    # Collect KPIs
    kpis = {
        "parts_produced": clone_factory.parts_produced,
        "total_downtime": clone_factory.total_downtime,
        "average_technicians": sum(scenario_schedule.values()) / len(scenario_schedule),
    }

    print(f"\nScenario complete!")
    print(f"  Parts produced:   {kpis['parts_produced']}")
    print(f"  Total downtime:   {kpis['total_downtime']:.1f} minutes")
    print(f"  Avg technicians:  {kpis['average_technicians']:.1f}")

    return kpis


# ========================================================================================
# MAIN PREDICTIVE WORKFLOW
# ========================================================================================

def operator_process(env, factory):
    """
    Operator decision-making process.

    This process waits for a decision point, then triggers predictive analysis
    by forking the simulation into multiple scenarios.

    Args:
        env: Real-time SimPy environment
        factory: Base factory instance
    """
    # Wait for decision point (real seconds)
    print(f"\n[Operator] Monitoring base twin... decision point in {DECISION_POINT} seconds\n")
    yield env.timeout(DECISION_POINT / REALTIME_FACTOR)  # Convert real seconds to sim time

    print("\n" + "="*70)
    print("⏸ OPERATOR: Pausing base twin for 'What-If' analysis")
    print("="*70)

    # Save current state
    saved_state = factory.save_state()

    print("\nState snapshot captured:")
    print(f"  Simulation time:  {saved_state['simulation_time']:.1f} minutes")
    print(f"  Parts in queue:   {saved_state['parts_in_queue']}")
    print(f"  Machine state:    {saved_state['machine_state']}")
    print(f"  Parts produced:   {saved_state['parts_produced']}")
    print(f"  Total downtime:   {saved_state['total_downtime']:.1f} minutes")

    print("\n" + "="*70)
    print("🔮 LAUNCHING PREDICTIVE CLONES")
    print("="*70)

    # Run baseline scenario (current plan)
    print("\n--- SCENARIO 1: Baseline (Current Shift Schedule) ---")
    baseline_kpis = run_predictive_clone(saved_state, SCENARIO_BASELINE, duration=480)

    # Run proposed scenario (alternative plan)
    print("\n--- SCENARIO 2: Proposed (Enhanced Shift Schedule) ---")
    proposed_kpis = run_predictive_clone(saved_state, SCENARIO_PROPOSED, duration=480)

    # Compare scenarios
    print("\n" + "="*70)
    print("📊 SCENARIO COMPARISON")
    print("="*70)

    print(f"\n{'Metric':<25} | {'Baseline':>12} | {'Proposed':>12} | {'Difference':>12}")
    print("-" * 70)

    # Parts produced
    diff_parts = proposed_kpis['parts_produced'] - baseline_kpis['parts_produced']
    print(f"{'Parts Produced':<25} | {baseline_kpis['parts_produced']:>12} | "
          f"{proposed_kpis['parts_produced']:>12} | {diff_parts:>+12}")

    # Downtime
    diff_downtime = proposed_kpis['total_downtime'] - baseline_kpis['total_downtime']
    print(f"{'Downtime (minutes)':<25} | {baseline_kpis['total_downtime']:>12.1f} | "
          f"{proposed_kpis['total_downtime']:>12.1f} | {diff_downtime:>+12.1f}")

    # Avg technicians
    diff_tech = proposed_kpis['average_technicians'] - baseline_kpis['average_technicians']
    print(f"{'Avg Technicians':<25} | {baseline_kpis['average_technicians']:>12.1f} | "
          f"{proposed_kpis['average_technicians']:>12.1f} | {diff_tech:>+12.1f}")

    print("\n" + "="*70)
    print("💡 DECISION RECOMMENDATION")
    print("="*70)

    if diff_parts > 0:
        improvement_pct = (diff_parts / baseline_kpis['parts_produced']) * 100
        downtime_reduction = -diff_downtime  # Negative means reduction

        print(f"\n✓ The PROPOSED schedule is predicted to:")
        print(f"  • Increase production by {diff_parts} parts ({improvement_pct:.1f}% improvement)")
        print(f"  • Reduce downtime by {downtime_reduction:.1f} minutes")
        print(f"  • Require {diff_tech:.1f} additional technicians on average")
        print(f"\n  RECOMMENDATION: Adopt the proposed shift schedule.")
    else:
        print(f"\n✗ The proposed schedule does NOT improve production.")
        print(f"  RECOMMENDATION: Keep the baseline schedule.")

    print("\n" + "="*70)


def main():
    """
    Main function: Run real-time base twin with predictive analysis.
    """
    print("\n" + "="*70)
    print("LAB 10: PREDICTIVE 'WHAT-IF' SCENARIO ANALYSIS")
    print("="*70)
    print("\nDemonstrating:")
    print("  1. Real-time base twin running for {:.0f} seconds".format(DECISION_POINT))
    print("  2. State snapshot at decision point")
    print("  3. Two FTRT clones exploring alternative futures")
    print("  4. KPI comparison for data-driven decisions")
    print("\n" + "="*70)

    # Set random seed for reproducibility
    random.seed(42)

    # Create real-time environment
    # factor < 1.0 means slower than wall-clock (more observable)
    rt_env = simpy.RealtimeEnvironment(factor=REALTIME_FACTOR, strict=False)

    # Create base factory (uses baseline schedule initially)
    base_factory = Factory(rt_env, SCENARIO_BASELINE, verbose=True)

    # Start operator process
    rt_env.process(operator_process(rt_env, base_factory))

    # Start base factory
    base_factory.run()

    # Run real-time simulation
    # This will run for DECISION_POINT real seconds, then operator triggers analysis
    try:
        rt_env.run(until=(DECISION_POINT / REALTIME_FACTOR) + 5)  # Run slightly past decision point
    except simpy.Interrupt:
        pass

    print("\n" + "="*70)
    print("✓ LAB 10 COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  • Digital Twins can 'fork' to explore alternative futures")
    print("  • FTRT simulations enable rapid scenario comparison")
    print("  • Data-driven decisions based on predicted outcomes")
    print("  • State management is key to forking capability")
    print("="*70 + "\n")


# ========================================================================================
# SCRIPT EXECUTION
# ========================================================================================

if __name__ == "__main__":
    main()
