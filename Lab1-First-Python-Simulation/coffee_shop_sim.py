"""
Lab 1: Building Your First Simulation in Python
Coffee Shop Single-Server Queue Simulation

This script implements a discrete-event simulation of a single-server queuing system
(a coffee shop with one barista) using basic Python programming without any simulation frameworks.

Learning Objectives:
- Understand how loops and variables can drive a simulation
- Learn to generate random arrivals and service times
- Calculate queue performance metrics (wait time, utilization, etc.)
- See the relationship between server utilization and customer wait times
"""

import random
import math

# --- Input Parameters ---
# These parameters define the behavior of our queuing system
MEAN_INTERARRIVAL_TIME = 3.0  # Average time (in minutes) between customer arrivals
MIN_SERVICE_TIME = 2.0        # Minimum time (in minutes) for the barista to make a drink
MAX_SERVICE_TIME = 5.0        # Maximum time (in minutes) for the barista to make a drink
NUM_CUSTOMERS_TO_SIMULATE = 100  # Number of customers to simulate

# Optional: Set a seed for reproducibility (comment out for true randomness)
# random.seed(42)

# --- State Variables and Result Lists ---
# These variables track the state of the system from one customer to the next
time_of_previous_arrival = 0.0
time_server_is_free = 0.0  # This is the same as the "Time Service Ends" of the previous customer

# These lists will store the results for each customer for later analysis
wait_times = []
times_in_system = []
server_idle_periods = []
arrival_times = []
service_times = []

# --- Main Simulation Loop ---
print(f"--- Simulating {NUM_CUSTOMERS_TO_SIMULATE} Customers ---")

for customer_num in range(1, NUM_CUSTOMERS_TO_SIMULATE + 1):
    # 1. Calculate Inter-Arrival Time and this customer's Arrival Time
    # Using exponential distribution: -ln(U) * mean
    # This models random arrivals (Poisson process)
    interarrival_time = -math.log(random.random()) * MEAN_INTERARRIVAL_TIME
    arrival_time = time_of_previous_arrival + interarrival_time

    # 2. Calculate Service Time for this customer
    # Using uniform distribution between min and max
    service_time = random.uniform(MIN_SERVICE_TIME, MAX_SERVICE_TIME)

    # 3. Calculate when service begins for this customer
    # This is the core logic of the queue!
    # Service begins at the later of two times:
    #   - When the customer arrives, OR
    #   - When the server becomes free
    # If the server is busy when the customer arrives, they must wait!
    time_service_begins = max(arrival_time, time_server_is_free)

    # 4. Calculate key metrics for this customer
    wait_in_queue = time_service_begins - arrival_time  # How long they waited
    time_service_ends = time_service_begins + service_time  # When service completes
    time_in_system = time_service_ends - arrival_time  # Total time (wait + service)
    server_idle_time = time_service_begins - time_server_is_free  # How long server was idle before this customer

    # 5. Store the results in our lists
    wait_times.append(wait_in_queue)
    times_in_system.append(time_in_system)
    server_idle_periods.append(server_idle_time)
    arrival_times.append(arrival_time)
    service_times.append(service_time)

    # 6. Update the state variables for the *next* customer's arrival
    time_of_previous_arrival = arrival_time
    time_server_is_free = time_service_ends

# --- Calculate and Display Output KPIs ---

# Calculate Average Wait Time
avg_wait_time = sum(wait_times) / len(wait_times)

# Calculate Probability of Waiting
customers_who_waited = len([w for w in wait_times if w > 0])
prob_wait = customers_who_waited / NUM_CUSTOMERS_TO_SIMULATE

# Calculate Server Utilization
total_simulation_time = time_server_is_free  # Time the last customer leaves
total_idle_time = sum(server_idle_periods)
total_busy_time = total_simulation_time - total_idle_time
server_utilization = total_busy_time / total_simulation_time

# Calculate other metrics
avg_time_in_system = sum(times_in_system) / len(times_in_system)
max_wait_time = max(wait_times)
avg_service_time = sum(service_times) / len(service_times)

# Print the results in a clean format
print("\n" + "="*50)
print("           SIMULATION RESULTS")
print("="*50)
print(f"\nInput Parameters:")
print(f"  Mean Interarrival Time: {MEAN_INTERARRIVAL_TIME:.2f} minutes")
print(f"  Service Time Range:     {MIN_SERVICE_TIME:.2f} - {MAX_SERVICE_TIME:.2f} minutes")
print(f"  Number of Customers:    {NUM_CUSTOMERS_TO_SIMULATE}")
print(f"\nPerformance Metrics:")
print(f"  Average Wait Time:      {avg_wait_time:.2f} minutes")
print(f"  Maximum Wait Time:      {max_wait_time:.2f} minutes")
print(f"  Probability of Waiting: {prob_wait:.2%}")
print(f"  Server Utilization:     {server_utilization:.2%}")
print(f"  Average Time in System: {avg_time_in_system:.2f} minutes")
print(f"  Average Service Time:   {avg_service_time:.2f} minutes")
print(f"\nSimulation Statistics:")
print(f"  Total Simulation Time:  {total_simulation_time:.2f} minutes")
print(f"  Total Server Busy Time: {total_busy_time:.2f} minutes")
print(f"  Total Server Idle Time: {total_idle_time:.2f} minutes")
print("="*50)

# --- Optional: Show first few customers in detail ---
print("\nFirst 10 Customers (detailed):")
print(f"{'Cust':<6}{'Arrival':<10}{'Wait':<10}{'Service':<10}{'In System':<12}")
print("-" * 50)
for i in range(min(10, NUM_CUSTOMERS_TO_SIMULATE)):
    print(f"{i+1:<6}{arrival_times[i]:<10.2f}{wait_times[i]:<10.2f}"
          f"{service_times[i]:<10.2f}{times_in_system[i]:<12.2f}")
