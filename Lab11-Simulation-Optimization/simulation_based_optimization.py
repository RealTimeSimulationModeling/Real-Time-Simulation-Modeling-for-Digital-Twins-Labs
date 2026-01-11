"""
Lab 11: Simulation-Based Optimization
======================================

Demonstrates prescriptive analytics using simulation-based optimization.
Uses a stochastic inventory management simulation as an objective function
for a powerful evolutionary optimizer to find optimal operational parameters.

This shows how Digital Twins enable not just prediction (descriptive/predictive)
but also prescription (what SHOULD we do to optimize performance).

Prerequisites:
    - simpy (discrete event simulation)
    - scipy (optimization algorithms)
    - numpy (numerical computing)

Usage:
    python simulation_based_optimization.py

What to observe:
    - Optimizer explores different (s,S) policies
    - Each evaluation runs multiple simulation replications
    - Evolutionary algorithm converges to optimal parameters
    - Final recommendation: best inventory control policy
"""

import simpy
import random
import numpy as np
from scipy.optimize import differential_evolution
import time


# ========================================================================================
# COST PARAMETERS
# ========================================================================================

# These define the trade-offs the optimizer must balance
HOLDING_COST_PER_ITEM_DAY = 0.50  # $ per item per day in inventory
ORDERING_COST = 100.0              # $ fixed cost per order placed
STOCKOUT_COST_PER_ITEM = 20.0      # $ penalty per lost sale

# Simulation parameters
SIMULATION_DAYS = 365  # Simulate one year of operations
INITIAL_INVENTORY = 200  # Starting inventory level

# Demand parameters (stochastic customer orders)
CUSTOMER_ARRIVAL_RATE = 2.0  # Mean customers per day (exponential)
ORDER_SIZE_MIN = 1           # Minimum order size
ORDER_SIZE_MAX = 10          # Maximum order size

# Supply chain parameters (stochastic lead time)
LEAD_TIME_MIN = 3.0  # Minimum days for replenishment
LEAD_TIME_MAX = 7.0  # Maximum days for replenishment

# Optimization parameters
N_REPLICATIONS = 5  # Number of simulation runs per policy evaluation
                    # More replications = more stable but slower


# ========================================================================================
# INVENTORY SIMULATION MODEL
# ========================================================================================

class InventorySystem:
    """
    Stochastic inventory management simulation.

    Implements (s,S) policy:
    - When inventory drops below s (reorder point), place order
    - Order quantity brings inventory up to S (order-up-to level)

    Tracks three costs:
    - Holding: Cost of keeping items in inventory
    - Ordering: Fixed cost per order placed
    - Stockout: Penalty for lost sales
    """

    def __init__(self, env, s, S, verbose=False):
        """
        Initialize inventory system.

        Args:
            env: SimPy environment
            s: Reorder point (trigger level)
            S: Order-up-to level (target inventory)
            verbose: Print detailed logs
        """
        self.env = env
        self.s = s  # Decision variable 1
        self.S = S  # Decision variable 2
        self.verbose = verbose

        # Inventory (SimPy container)
        # Initialize with minimum of INITIAL_INVENTORY and S (can't exceed capacity)
        initial_level = min(INITIAL_INVENTORY, S)
        self.inventory = simpy.Container(env, capacity=S, init=initial_level)

        # Cost tracking
        self.total_holding_cost = 0.0
        self.total_ordering_cost = 0.0
        self.total_stockout_cost = 0.0

        # Statistics
        self.orders_placed = 0
        self.units_sold = 0
        self.stockouts_count = 0
        self.lost_sales_units = 0

        # For calculating average inventory
        self.inventory_levels = []
        self.inventory_times = []

    def _log(self, message):
        """Print log if verbose mode enabled."""
        if self.verbose:
            print(f"[Day {self.env.now:6.1f}] {message}")

    def customer_process(self):
        """
        Generate customer demand (stochastic arrivals and order sizes).

        Customers arrive randomly and request random quantities.
        If inventory is insufficient, it's a stockout (lost sale).
        """
        while True:
            # Wait for next customer arrival (exponential inter-arrival time)
            inter_arrival = random.expovariate(CUSTOMER_ARRIVAL_RATE)
            yield self.env.timeout(inter_arrival)

            # Customer places order (random size)
            order_size = random.randint(ORDER_SIZE_MIN, ORDER_SIZE_MAX)

            # Try to fulfill order
            available = self.inventory.level
            if available >= order_size:
                # Sufficient inventory - fulfill order
                yield self.inventory.get(order_size)
                self.units_sold += order_size
                self._log(f"Customer: Sold {order_size} units (Inv: {self.inventory.level})")

            else:
                # Stockout - lost sale
                self.stockouts_count += 1
                lost_units = order_size - available

                # Sell whatever we have
                if available > 0:
                    yield self.inventory.get(available)
                    self.units_sold += available

                self.lost_sales_units += lost_units

                # Incur stockout penalty
                stockout_penalty = lost_units * STOCKOUT_COST_PER_ITEM
                self.total_stockout_cost += stockout_penalty

                self._log(f"Customer: STOCKOUT! Wanted {order_size}, had {available}, "
                         f"lost {lost_units} units (Penalty: ${stockout_penalty:.2f})")

    def inventory_control_process(self):
        """
        Inventory control using (s,S) policy.

        Monitors inventory level:
        - When level drops below s: Place replenishment order
        - Order quantity: S - current_level (bring up to S)
        - After random lead time, inventory arrives
        """
        while True:
            # Check inventory level
            current_level = self.inventory.level

            if current_level < self.s:
                # Below reorder point - place order!
                order_qty = self.S - current_level

                # Incur fixed ordering cost
                self.total_ordering_cost += ORDERING_COST
                self.orders_placed += 1

                self._log(f"Control: Inventory {current_level:.1f} < {self.s:.1f} (reorder point)")
                self._log(f"Control: Placing order for {order_qty:.1f} units (Cost: ${ORDERING_COST})")

                # Wait for random lead time
                lead_time = random.uniform(LEAD_TIME_MIN, LEAD_TIME_MAX)
                yield self.env.timeout(lead_time)

                # Order arrives - add to inventory
                try:
                    yield self.inventory.put(order_qty)
                    self._log(f"Control: Order arrived ({order_qty:.1f} units). "
                             f"New inventory: {self.inventory.level:.1f}")
                except simpy.ContainerOverflow:
                    # Can't exceed capacity (shouldn't happen with proper S setting)
                    actual_qty = self.inventory.capacity - self.inventory.level
                    yield self.inventory.put(actual_qty)
                    self._log(f"Control: Order partially received (capacity limit)")

                # Don't immediately reorder - wait a bit
                yield self.env.timeout(0.1)

            else:
                # Inventory above reorder point - check again later
                yield self.env.timeout(1.0)  # Check daily

    def monitoring_process(self):
        """
        Monitor inventory levels for calculating holding cost.

        Records inventory level over time to compute time-weighted average.
        Holding cost = average_inventory * cost_per_item_day * simulation_days
        """
        while True:
            # Record current inventory level and time
            self.inventory_levels.append(self.inventory.level)
            self.inventory_times.append(self.env.now)

            # Check daily
            yield self.env.timeout(1.0)

    def calculate_total_cost(self):
        """
        Calculate total cost after simulation completes.

        Returns:
            float: Total cost (holding + ordering + stockout)
        """
        # Calculate time-weighted average inventory
        if len(self.inventory_levels) > 1:
            # Use trapezoidal rule for integration
            avg_inventory = np.trapz(self.inventory_levels, self.inventory_times) / self.env.now
        else:
            avg_inventory = INITIAL_INVENTORY

        # Calculate holding cost
        # Cost per item per day × average inventory × simulation duration
        self.total_holding_cost = HOLDING_COST_PER_ITEM_DAY * avg_inventory * self.env.now

        # Total cost is sum of all three components
        total_cost = (self.total_holding_cost +
                     self.total_ordering_cost +
                     self.total_stockout_cost)

        return total_cost

    def run_simulation(self, until=SIMULATION_DAYS):
        """
        Run the inventory simulation.

        Args:
            until: Simulation duration (days)

        Returns:
            float: Total cost incurred
        """
        # Start all processes
        self.env.process(self.customer_process())
        self.env.process(self.inventory_control_process())
        self.env.process(self.monitoring_process())

        # Run simulation
        self.env.run(until=until)

        # Calculate and return total cost
        return self.calculate_total_cost()


# ========================================================================================
# OPTIMIZATION WRAPPER (OBJECTIVE FUNCTION)
# ========================================================================================

# Global counter for tracking function evaluations
evaluation_counter = 0


def objective_function(decision_variables):
    """
    Objective function for optimizer.

    This is the bridge between the optimization algorithm and the simulation model.
    Takes candidate policy parameters, runs stochastic simulation multiple times,
    and returns average cost.

    Args:
        decision_variables: Array [s, S] - reorder point and order-up-to level

    Returns:
        float: Average total cost across replications (lower is better)
    """
    global evaluation_counter
    evaluation_counter += 1

    # Unpack decision variables
    s, S = decision_variables

    # CONSTRAINT ENFORCEMENT: s must be less than S
    if s >= S:
        # Invalid policy - return very high penalty cost
        return 1e9

    # Additional constraint: Ensure both are positive
    if s < 0 or S < 0:
        return 1e9

    # RUN MULTIPLE REPLICATIONS
    # Because simulation is stochastic, we need multiple runs to get stable average
    replication_costs = []

    for rep in range(N_REPLICATIONS):
        # Set different random seed for each replication
        random.seed(42 + evaluation_counter * 1000 + rep)

        # Create new simulation environment
        env = simpy.Environment()

        # Create inventory system with these parameters
        inv_system = InventorySystem(env, s=s, S=S, verbose=False)

        # Run simulation and get total cost
        cost = inv_system.run_simulation(until=SIMULATION_DAYS)

        # Store result
        replication_costs.append(cost)

    # Calculate average cost across replications
    avg_cost = np.mean(replication_costs)
    std_cost = np.std(replication_costs)

    # Log progress
    print(f"Eval {evaluation_counter:4d}: (s={s:6.1f}, S={S:6.1f}) → "
          f"Cost: ${avg_cost:10,.2f} ± ${std_cost:7,.2f}")

    # Return average cost (optimizer will minimize this)
    return avg_cost


# ========================================================================================
# OPTIMIZATION ENGINE
# ========================================================================================

def run_optimization():
    """
    Run simulation-based optimization using differential evolution.

    Differential evolution is a population-based stochastic optimizer
    (similar to genetic algorithms) that's well-suited for noisy,
    non-convex objective functions like simulation models.

    Returns:
        OptimizeResult: Optimization results including optimal parameters
    """
    print("\n" + "="*80)
    print("SIMULATION-BASED OPTIMIZATION: Finding Optimal Inventory Policy")
    print("="*80)

    print("\nProblem Setup:")
    print(f"  Decision Variables: (s, S)")
    print(f"    s = Reorder point (when to order)")
    print(f"    S = Order-up-to level (target inventory)")
    print(f"\n  Objective: Minimize total cost")
    print(f"    Holding cost:  ${HOLDING_COST_PER_ITEM_DAY}/item/day")
    print(f"    Ordering cost: ${ORDERING_COST}/order")
    print(f"    Stockout cost: ${STOCKOUT_COST_PER_ITEM}/lost unit")
    print(f"\n  Simulation: {SIMULATION_DAYS} days, {N_REPLICATIONS} replications per evaluation")

    # Define search bounds for decision variables
    # s: reorder point (10 to 150)
    # S: order-up-to level (100 to 500)
    bounds = [
        (10, 150),   # s bounds
        (100, 500),  # S bounds
    ]

    print(f"\n  Search Space:")
    print(f"    s ∈ [{bounds[0][0]}, {bounds[0][1]}]")
    print(f"    S ∈ [{bounds[1][0]}, {bounds[1][1]}]")

    print("\n" + "="*80)
    print("Starting Differential Evolution Optimizer...")
    print("="*80)
    print()

    # Start timer
    start_time = time.time()

    # Run differential evolution optimizer
    result = differential_evolution(
        func=objective_function,          # Function to minimize
        bounds=bounds,                    # Search space
        strategy='best1bin',              # DE strategy
        maxiter=30,                       # Maximum iterations (generations)
        popsize=10,                       # Population size (10 * 2 vars = 20 individuals)
        tol=0.01,                         # Tolerance for convergence
        atol=100,                         # Absolute tolerance
        mutation=(0.5, 1.5),             # Mutation factor range
        recombination=0.7,               # Crossover probability
        seed=42,                         # Random seed for reproducibility
        disp=True,                       # Display progress
        polish=True,                     # Local optimization at end
        workers=1,                       # Use single worker (simulation not thread-safe)
        updating='deferred',             # Update population after full generation
    )

    # End timer
    elapsed_time = time.time() - start_time

    print("\n" + "="*80)
    print("Optimization Complete!")
    print("="*80)

    # Extract results
    optimal_s = result.x[0]
    optimal_S = result.x[1]
    minimum_cost = result.fun

    print(f"\nOptimization Summary:")
    print(f"  Total evaluations: {evaluation_counter}")
    print(f"  Time elapsed:      {elapsed_time:.1f} seconds")
    print(f"  Convergence:       {'Success' if result.success else 'Did not converge'}")

    print(f"\n" + "="*80)
    print("OPTIMAL POLICY FOUND")
    print("="*80)
    print(f"\n  Reorder Point (s):     {optimal_s:6.1f} units")
    print(f"  Order-up-to Level (S): {optimal_S:6.1f} units")
    print(f"\n  Minimum Average Cost:  ${minimum_cost:,.2f} per year")

    # Run one final detailed simulation with optimal parameters to show breakdown
    print(f"\n" + "="*80)
    print("Cost Breakdown (using optimal policy):")
    print("="*80)

    random.seed(42)
    env = simpy.Environment()
    final_system = InventorySystem(env, s=optimal_s, S=optimal_S, verbose=False)
    final_cost = final_system.run_simulation(until=SIMULATION_DAYS)

    print(f"\n  Holding Cost:   ${final_system.total_holding_cost:10,.2f} "
          f"({final_system.total_holding_cost/final_cost*100:.1f}%)")
    print(f"  Ordering Cost:  ${final_system.total_ordering_cost:10,.2f} "
          f"({final_system.total_ordering_cost/final_cost*100:.1f}%)")
    print(f"  Stockout Cost:  ${final_system.total_stockout_cost:10,.2f} "
          f"({final_system.total_stockout_cost/final_cost*100:.1f}%)")
    print(f"  {'-'*60}")
    print(f"  Total Cost:     ${final_cost:10,.2f}")

    print(f"\n  Operational Statistics:")
    print(f"    Orders placed:   {final_system.orders_placed}")
    print(f"    Units sold:      {final_system.units_sold}")
    print(f"    Stockouts:       {final_system.stockouts_count}")
    print(f"    Lost sales:      {final_system.lost_sales_units} units")

    print(f"\n" + "="*80)
    print("PRESCRIPTIVE RECOMMENDATION")
    print("="*80)
    print(f"\n  Implement the (s,S) policy with:")
    print(f"    • Reorder when inventory drops below {optimal_s:.0f} units")
    print(f"    • Order enough to bring inventory to {optimal_S:.0f} units")
    print(f"\n  Expected annual cost: ${minimum_cost:,.2f}")
    print(f"\n  This policy optimally balances:")
    print(f"    • Keeping enough inventory to avoid stockouts")
    print(f"    • Minimizing holding costs by not over-stocking")
    print(f"    • Reducing ordering frequency to minimize fixed costs")

    print("\n" + "="*80)

    return result


# ========================================================================================
# MAIN EXECUTION
# ========================================================================================

def main():
    """
    Main function: Run simulation-based optimization.
    """
    print("\n" + "="*80)
    print("LAB 11: SIMULATION-BASED OPTIMIZATION")
    print("="*80)
    print("\nDemonstrating:")
    print("  • Using simulation as objective function for optimization")
    print("  • Handling stochastic objective functions with replications")
    print("  • Finding optimal operational parameters automatically")
    print("  • Prescriptive analytics: What SHOULD we do?")

    # Run optimization
    result = run_optimization()

    print("\n" + "="*80)
    print("KEY TAKEAWAYS")
    print("="*80)
    print("\n  1. DESCRIPTIVE: Simulation describes what happens with given parameters")
    print("  2. PREDICTIVE: Running simulation predicts future performance")
    print("  3. PRESCRIPTIVE: Optimization prescribes the BEST parameters to use")
    print("\n  Digital Twins enable moving from observation to optimal action!")

    print("\n" + "="*80)
    print("✓ LAB 11 COMPLETE")
    print("="*80 + "\n")

    return result


# ========================================================================================
# SCRIPT EXECUTION
# ========================================================================================

if __name__ == "__main__":
    # Set numpy random seed for reproducibility
    np.random.seed(42)

    # Run optimization
    result = main()
