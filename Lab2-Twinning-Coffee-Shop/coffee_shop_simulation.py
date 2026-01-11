"""
Lab 2: Twinning a Coffee Shop - Discrete Event Simulation
==========================================================

This script implements a three-phase discrete-event simulation (DES) of a coffee shop
using the SimPy library, demonstrating the foundational concepts of digital twins.

Phases:
    1. Foundational DES Model: Standard stochastic simulation
    2. Instrumentation for Twinning: Dynamic parameter modification
    3. Simulating Real-Time Connection: External control process

DES Concepts Demonstrated:
    - Entities: Customer objects with unique IDs
    - Resources: Barista resources managed via simpy.Store
    - Queues: Implicit queuing when all baristas are busy
    - Process-Interaction Worldview: Customer lifecycle processes
    - Stochastic Events: Exponential arrivals, Triangular service times
"""

import simpy
import random
import threading
import time
from statistics import mean

# ========================================================================================
# PHASE 1: FOUNDATIONAL DES MODEL - CONFIGURATION
# ========================================================================================

# Simulation Parameters
RANDOM_SEED = 42               # For reproducibility
NUM_BARISTAS = 2               # Initial number of barista resources
SIM_TIME = 100                 # Simulation time units (minutes)
INITIAL_MEAN_INTERARRIVAL = 5  # Mean time between customer arrivals (minutes)

# Service Time Distribution Parameters (Triangular)
SERVICE_TIME_MIN = 2           # Minimum service time (minutes)
SERVICE_TIME_MODE = 3          # Most likely service time (minutes)
SERVICE_TIME_MAX = 5           # Maximum service time (minutes)


# ========================================================================================
# PHASE 1 & 2: COFFEE SHOP CLASS - DES MODEL WITH INSTRUMENTATION
# ========================================================================================

class CoffeeShop:
    """
    Encapsulates the discrete-event simulation of a coffee shop.

    This class represents the simulation model, managing:
    - The SimPy environment (simulation clock and event scheduler)
    - Barista resources (using simpy.Store for dynamic capacity)
    - Customer generation and processing
    - Data collection for statistics

    Phase 2 adds instrumentation methods for dynamic parameter updates.
    """

    def __init__(self, env, num_baristas, mean_interarrival):
        """
        Initialize the coffee shop simulation environment.

        Args:
            env: SimPy environment instance
            num_baristas: Initial number of barista resources
            mean_interarrival: Mean time between customer arrivals (exponential distribution)
        """
        # Core simulation components
        self.env = env

        # RESOURCE MANAGEMENT (Phase 2 design):
        # Using simpy.Store instead of simpy.Resource allows dynamic capacity changes
        # Each barista is an object in the store that can be "seized" (get) and "released" (put)
        self.barista_store = simpy.Store(env)

        # Populate the store with initial baristas
        for i in range(num_baristas):
            self.barista_store.put(f"Barista_{i+1}")

        # DYNAMIC PARAMETERS (Phase 2 instrumentation):
        # These can be modified during simulation runtime
        self.mean_interarrival = mean_interarrival
        self.current_barista_count = num_baristas

        # DATA COLLECTION:
        # Store metrics for final analysis
        self.wait_times = []           # Customer waiting times
        self.customers_served = 0       # Total customers who completed service
        self.customer_counter = 0       # For generating unique customer IDs

        # Thread safety lock for shared data access
        self.lock = threading.Lock()

    # ====================================================================================
    # PHASE 1: CORE SIMULATION PROCESSES
    # ====================================================================================

    def customer(self, customer_id):
        """
        Defines the lifecycle of a single customer entity (Process-Interaction Worldview).

        Customer Process Flow:
            1. Arrive at coffee shop
            2. Request (seize) a barista resource
            3. Wait in queue if all baristas are busy (implicit in Store.get())
            4. Receive service (modeled as a time delay)
            5. Release the barista resource
            6. Leave the system

        Args:
            customer_id: Unique identifier for this customer entity
        """
        # EVENT 1: ARRIVAL
        arrival_time = self.env.now
        print(f"[{self.env.now:6.2f}] Customer {customer_id:3d} | ARRIVES")

        # EVENT 2: REQUEST BARISTA (Resource Seize)
        # The customer attempts to "get" a barista from the store
        # If no baristas are available, this creates an implicit queue (customer waits)
        barista = yield self.barista_store.get()

        # EVENT 3: SERVICE BEGINS
        # Calculate wait time (time from arrival until service starts)
        wait_time = self.env.now - arrival_time

        with self.lock:
            self.wait_times.append(wait_time)

        print(f"[{self.env.now:6.2f}] Customer {customer_id:3d} | STARTS SERVICE (waited {wait_time:.2f} min) with {barista}")

        # EVENT 4: SERVICE DELAY
        # Service time follows a Triangular distribution (min, mode, max)
        # This represents the stochastic nature of real-world service times
        service_time = random.triangular(SERVICE_TIME_MIN, SERVICE_TIME_MAX, SERVICE_TIME_MODE)
        yield self.env.timeout(service_time)

        # EVENT 5: RELEASE BARISTA (Resource Release)
        # Customer is done, put the barista back in the store for the next customer
        yield self.barista_store.put(barista)

        # EVENT 6: DEPARTURE
        print(f"[{self.env.now:6.2f}] Customer {customer_id:3d} | LEAVES (service took {service_time:.2f} min)")

        with self.lock:
            self.customers_served += 1

    def setup(self):
        """
        Customer generator process (Entity Creation).

        This is the main driver of the simulation. It continuously creates new
        customer entities at stochastic intervals following an exponential distribution.

        The exponential distribution models random, memoryless arrivals (Poisson process),
        which is appropriate for modeling customer arrivals in service systems.
        """
        print("\n" + "="*80)
        print("COFFEE SHOP SIMULATION STARTING")
        print("="*80)
        print(f"Configuration: {self.current_barista_count} baristas, "
              f"mean inter-arrival = {self.mean_interarrival:.2f} min")
        print("="*80 + "\n")

        while True:
            # Generate inter-arrival time (exponentially distributed)
            # This represents the time until the next customer arrives
            interarrival_time = random.expovariate(1.0 / self.mean_interarrival)

            # Wait for the next arrival
            yield self.env.timeout(interarrival_time)

            # Check if we've exceeded the simulation time
            if self.env.now > SIM_TIME:
                break

            # Create a new customer entity
            with self.lock:
                self.customer_counter += 1
                customer_id = self.customer_counter

            # Start the customer's process
            self.env.process(self.customer(customer_id))

    # ====================================================================================
    # PHASE 2: INSTRUMENTATION METHODS FOR TWINNING
    # ====================================================================================

    def set_arrival_rate(self, new_mean_interarrival):
        """
        Dynamically adjust the customer arrival rate during simulation.

        This represents updating the simulation based on real-time data.
        For example, a sensor might detect increased foot traffic, or
        historical data might indicate a lunch rush is starting.

        Args:
            new_mean_interarrival: New mean time between arrivals (minutes)
        """
        with self.lock:
            old_rate = self.mean_interarrival
            self.mean_interarrival = new_mean_interarrival

        print(f"\n{'*'*80}")
        print(f"[{self.env.now:6.2f}] CONTROL EVENT | Arrival rate changed: "
              f"{old_rate:.2f} min -> {new_mean_interarrival:.2f} min")
        print(f"{'*'*80}\n")

    def add_barista(self):
        """
        Dynamically add a new barista resource during simulation.

        This simulates real-world events like a new employee starting their shift
        or additional staff being called in during peak hours.

        Implementation: Adds a new barista object to the resource store.
        """
        with self.lock:
            self.current_barista_count += 1
            new_barista_id = self.current_barista_count

        # Add the new barista to the store (becomes immediately available)
        self.barista_store.put(f"Barista_{new_barista_id}")

        print(f"\n{'*'*80}")
        print(f"[{self.env.now:6.2f}] CONTROL EVENT | New barista added (Barista_{new_barista_id}). "
              f"Total baristas: {self.current_barista_count}")
        print(f"{'*'*80}\n")

    def remove_barista(self):
        """
        Dynamically remove a barista resource during simulation.

        This simulates events like an employee going on break or ending their shift.

        IMPORTANT: We don't forcibly remove a barista who is serving a customer.
        Instead, we request a barista from the store. This ensures the barista
        finishes their current service before being removed (realistic behavior).
        """
        print(f"\n{'*'*80}")
        print(f"[{self.env.now:6.2f}] CONTROL EVENT | Attempting to remove a barista...")
        print(f"{'*'*80}\n")

        # This will wait if all baristas are busy (realistic - can't remove a busy barista)
        def removal_process():
            barista = yield self.barista_store.get()
            with self.lock:
                self.current_barista_count -= 1

            print(f"\n{'*'*80}")
            print(f"[{self.env.now:6.2f}] CONTROL EVENT | Barista removed ({barista}). "
                  f"Total baristas: {self.current_barista_count}")
            print(f"{'*'*80}\n")

        self.env.process(removal_process())

    # ====================================================================================
    # STATISTICS AND REPORTING
    # ====================================================================================

    def print_statistics(self):
        """
        Calculate and display final simulation statistics.
        """
        print("\n" + "="*80)
        print("SIMULATION COMPLETE - FINAL STATISTICS")
        print("="*80)
        print(f"Simulation Time:          {SIM_TIME} minutes")
        print(f"Customers Served:         {self.customers_served}")
        print(f"Final Barista Count:      {self.current_barista_count}")

        if self.wait_times:
            avg_wait = mean(self.wait_times)
            max_wait = max(self.wait_times)
            min_wait = min(self.wait_times)
            print(f"\nWaiting Time Statistics:")
            print(f"  Average Wait Time:      {avg_wait:.2f} minutes")
            print(f"  Maximum Wait Time:      {max_wait:.2f} minutes")
            print(f"  Minimum Wait Time:      {min_wait:.2f} minutes")
        else:
            print("\nNo customers were served during the simulation.")

        print("="*80 + "\n")


# ========================================================================================
# PHASE 3: SIMULATING A REAL-TIME CONNECTION
# ========================================================================================

def control_panel(coffee_shop):
    """
    Simulates an external control system or real-time data feed.

    This function runs in a separate thread and represents the "real world"
    sending updates to the simulation. In a true digital twin, this would be:
    - IoT sensor data (e.g., foot traffic counters)
    - Weather data affecting customer arrivals
    - Staff scheduling system updates
    - Point-of-sale system data

    This control process operates on "wall-clock" time (real seconds) while the
    simulation operates on "simulation time" (simulated minutes), demonstrating
    the asynchronous nature of digital twin systems.

    Args:
        coffee_shop: The CoffeeShop instance to control
    """
    print("\n[CONTROL PANEL] External control thread started (running in real-time)\n")

    # SCENARIO 1: Lunch rush begins (10 real seconds = simulation continues)
    time.sleep(10)
    print("\n[CONTROL PANEL] Real-time event detected: LUNCH RUSH STARTING!")
    coffee_shop.set_arrival_rate(2.0)  # Increase arrival rate (shorter inter-arrival)

    # SCENARIO 2: Additional barista comes on duty (5 seconds later)
    time.sleep(5)
    print("\n[CONTROL PANEL] Real-time event detected: NEW BARISTA SHIFT STARTING!")
    coffee_shop.add_barista()

    # SCENARIO 3: Lunch rush subsides (15 seconds later)
    time.sleep(15)
    print("\n[CONTROL PANEL] Real-time event detected: LUNCH RUSH ENDING!")
    coffee_shop.set_arrival_rate(6.0)  # Decrease arrival rate (longer inter-arrival)

    # SCENARIO 4: Barista goes on break (10 seconds later)
    time.sleep(10)
    print("\n[CONTROL PANEL] Real-time event detected: BARISTA GOING ON BREAK!")
    coffee_shop.remove_barista()

    print("\n[CONTROL PANEL] No more scheduled control events.\n")


# ========================================================================================
# MAIN EXECUTION
# ========================================================================================

def main():
    """
    Main execution function that orchestrates all three phases of the simulation.
    """
    # Set random seed for reproducibility
    random.seed(RANDOM_SEED)

    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  LAB 2: TWINNING A COFFEE SHOP - DISCRETE EVENT SIMULATION".center(78) + "║")
    print("║" + "  Three-Phase Implementation: DES + Instrumentation + Real-Time Control".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝")

    # PHASE 1 & 2: Initialize the simulation environment and coffee shop
    env = simpy.Environment()
    coffee_shop = CoffeeShop(env, NUM_BARISTAS, INITIAL_MEAN_INTERARRIVAL)

    # Start the customer generation process
    env.process(coffee_shop.setup())

    # PHASE 3: Start the external control thread
    # This thread simulates real-time data feeds that modify the simulation
    control_thread = threading.Thread(target=control_panel, args=(coffee_shop,))
    control_thread.daemon = True  # Thread will close when main program exits
    control_thread.start()

    # Run the simulation
    # The simulation will run until SIM_TIME, while the control thread
    # operates asynchronously in real-time
    env.run(until=SIM_TIME)

    # Display final statistics
    coffee_shop.print_statistics()

    # Give the control thread a moment to finish any final messages
    time.sleep(1)

    print("Simulation execution complete. Digital twin demonstration finished.\n")


if __name__ == "__main__":
    main()
