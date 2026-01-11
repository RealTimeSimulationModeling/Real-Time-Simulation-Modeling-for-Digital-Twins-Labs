"""
Lab 2: Twinning a Coffee Shop - REAL-TIME Discrete Event Simulation
====================================================================

This is an enhanced version that demonstrates real-time control by slowing down
the simulation to synchronize with wall-clock time. This makes the control panel
events visible and demonstrates true digital twin behavior.

Key Enhancement: RealtimeEnvironment
The simulation runs at a 1:10 speed ratio (1 real second = 10 simulation minutes)
allowing the control panel to interact with the simulation in observable time.
"""

import simpy
import simpy.rt  # Real-time simulation module
import random
import threading
import time
from statistics import mean

# ========================================================================================
# CONFIGURATION - REAL-TIME VERSION
# ========================================================================================

RANDOM_SEED = 42
NUM_BARISTAS = 2
SIM_TIME = 200                     # Extended simulation time
INITIAL_MEAN_INTERARRIVAL = 5

# Real-time simulation scaling: How many sim-minutes per real-second
# Setting this to 10 means: 1 real second = 10 simulation minutes
REALTIME_SCALE = 10

# Service Time Distribution Parameters
SERVICE_TIME_MIN = 2
SERVICE_TIME_MODE = 3
SERVICE_TIME_MAX = 5


# ========================================================================================
# COFFEE SHOP CLASS (Enhanced for Real-Time)
# ========================================================================================

class CoffeeShop:
    """
    Coffee shop simulation with real-time synchronization capabilities.
    """

    def __init__(self, env, num_baristas, mean_interarrival):
        self.env = env
        self.barista_store = simpy.Store(env)

        for i in range(num_baristas):
            self.barista_store.put(f"Barista_{i+1}")

        self.mean_interarrival = mean_interarrival
        self.current_barista_count = num_baristas
        self.wait_times = []
        self.customers_served = 0
        self.customer_counter = 0
        self.lock = threading.Lock()

    def customer(self, customer_id):
        """Customer lifecycle process."""
        arrival_time = self.env.now
        print(f"[{self.env.now:6.2f}] Customer {customer_id:3d} | ARRIVES")

        barista = yield self.barista_store.get()
        wait_time = self.env.now - arrival_time

        with self.lock:
            self.wait_times.append(wait_time)

        print(f"[{self.env.now:6.2f}] Customer {customer_id:3d} | STARTS SERVICE "
              f"(waited {wait_time:.2f} min) with {barista}")

        service_time = random.triangular(SERVICE_TIME_MIN, SERVICE_TIME_MAX, SERVICE_TIME_MODE)
        yield self.env.timeout(service_time)

        yield self.barista_store.put(barista)

        print(f"[{self.env.now:6.2f}] Customer {customer_id:3d} | LEAVES "
              f"(service took {service_time:.2f} min)")

        with self.lock:
            self.customers_served += 1

    def setup(self):
        """Customer generator process."""
        print("\n" + "="*80)
        print("COFFEE SHOP REAL-TIME SIMULATION STARTING")
        print("="*80)
        print(f"Configuration: {self.current_barista_count} baristas, "
              f"mean inter-arrival = {self.mean_interarrival:.2f} min")
        print(f"Real-time scale: 1 real second = {REALTIME_SCALE} simulation minutes")
        print("="*80 + "\n")

        while True:
            interarrival_time = random.expovariate(1.0 / self.mean_interarrival)
            yield self.env.timeout(interarrival_time)

            if self.env.now > SIM_TIME:
                break

            with self.lock:
                self.customer_counter += 1
                customer_id = self.customer_counter

            self.env.process(self.customer(customer_id))

    # Instrumentation methods (same as before)
    def set_arrival_rate(self, new_mean_interarrival):
        """Dynamically adjust customer arrival rate."""
        with self.lock:
            old_rate = self.mean_interarrival
            self.mean_interarrival = new_mean_interarrival

        print(f"\n{'*'*80}")
        print(f"[{self.env.now:6.2f}] CONTROL EVENT | Arrival rate changed: "
              f"{old_rate:.2f} min -> {new_mean_interarrival:.2f} min")
        print(f"{'*'*80}\n")

    def add_barista(self):
        """Dynamically add a new barista."""
        with self.lock:
            self.current_barista_count += 1
            new_barista_id = self.current_barista_count

        self.barista_store.put(f"Barista_{new_barista_id}")

        print(f"\n{'*'*80}")
        print(f"[{self.env.now:6.2f}] CONTROL EVENT | New barista added (Barista_{new_barista_id}). "
              f"Total baristas: {self.current_barista_count}")
        print(f"{'*'*80}\n")

    def remove_barista(self):
        """Dynamically remove a barista."""
        print(f"\n{'*'*80}")
        print(f"[{self.env.now:6.2f}] CONTROL EVENT | Attempting to remove a barista...")
        print(f"{'*'*80}\n")

        def removal_process():
            barista = yield self.barista_store.get()
            with self.lock:
                self.current_barista_count -= 1

            print(f"\n{'*'*80}")
            print(f"[{self.env.now:6.2f}] CONTROL EVENT | Barista removed ({barista}). "
                  f"Total baristas: {self.current_barista_count}")
            print(f"{'*'*80}\n")

        self.env.process(removal_process())

    def print_statistics(self):
        """Display final simulation statistics."""
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
# REAL-TIME CONTROL PANEL
# ========================================================================================

def control_panel(coffee_shop):
    """
    External control system running in real-time.

    Timeline (in real seconds):
    - t=3s: Lunch rush starts (increase arrival rate)
    - t=6s: New barista arrives
    - t=10s: Lunch rush ends (decrease arrival rate)
    - t=14s: Barista goes on break
    """
    print("\n[CONTROL PANEL] External control thread started\n")
    print("[CONTROL PANEL] Waiting for simulation to stabilize...\n")

    # Wait for simulation to get going
    time.sleep(3)
    print("\n[CONTROL PANEL] >>> Real-world event: LUNCH RUSH DETECTED! <<<")
    coffee_shop.set_arrival_rate(2.0)  # More customers (shorter inter-arrival)

    time.sleep(3)
    print("\n[CONTROL PANEL] >>> Real-world event: ADDITIONAL STAFF AVAILABLE <<<")
    coffee_shop.add_barista()

    time.sleep(4)
    print("\n[CONTROL PANEL] >>> Real-world event: LUNCH RUSH SUBSIDING <<<")
    coffee_shop.set_arrival_rate(7.0)  # Fewer customers (longer inter-arrival)

    time.sleep(4)
    print("\n[CONTROL PANEL] >>> Real-world event: STAFF BREAK TIME <<<")
    coffee_shop.remove_barista()

    print("\n[CONTROL PANEL] Control schedule complete. Monitoring continues...\n")


# ========================================================================================
# MAIN EXECUTION
# ========================================================================================

def main():
    """Main execution with real-time environment."""
    random.seed(RANDOM_SEED)

    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  LAB 2: COFFEE SHOP DIGITAL TWIN - REAL-TIME VERSION".center(78) + "║")
    print("║" + "  Demonstrating Synchronous Control and Simulation".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝")

    # Create REAL-TIME environment
    # The factor parameter controls the speed: how fast simulation time passes
    # relative to real time. factor=1/REALTIME_SCALE means slow down the simulation.
    env = simpy.rt.RealtimeEnvironment(factor=1/REALTIME_SCALE, strict=False)

    coffee_shop = CoffeeShop(env, NUM_BARISTAS, INITIAL_MEAN_INTERARRIVAL)
    env.process(coffee_shop.setup())

    # Start the control panel in a separate thread
    control_thread = threading.Thread(target=control_panel, args=(coffee_shop,))
    control_thread.daemon = True
    control_thread.start()

    try:
        # Run the simulation
        print("\n[INFO] Simulation running in REAL-TIME mode...")
        print("[INFO] You'll see control events happening as time progresses...\n")
        env.run(until=SIM_TIME)
    except KeyboardInterrupt:
        print("\n\n[INFO] Simulation interrupted by user.")

    coffee_shop.print_statistics()

    time.sleep(1)
    print("Real-time digital twin demonstration complete.\n")


if __name__ == "__main__":
    main()
