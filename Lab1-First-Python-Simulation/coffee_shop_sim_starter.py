"""
Lab 1: Building Your First Simulation in Python - STARTER TEMPLATE
Coffee Shop Single-Server Queue Simulation

Complete the TODOs below to build your first discrete-event simulation!
"""

import random
import math

# --- Input Parameters ---
# TODO: Define your simulation parameters here
MEAN_INTERARRIVAL_TIME = 3.0  # Average time (in minutes) between customer arrivals
MIN_SERVICE_TIME = 2.0        # Minimum time (in minutes) for the barista to make a drink
MAX_SERVICE_TIME = 5.0        # Maximum time (in minutes) for the barista to make a drink
NUM_CUSTOMERS_TO_SIMULATE = 100

# --- State Variables and Result Lists ---
# TODO: Initialize state variables to track the simulation
time_of_previous_arrival = 0.0
time_server_is_free = 0.0

# TODO: Create empty lists to store results for each customer
wait_times = []
times_in_system = []
server_idle_periods = []

# --- Main Simulation Loop ---
print(f"--- Simulating {NUM_CUSTOMERS_TO_SIMULATE} Customers ---")

for customer_num in range(1, NUM_CUSTOMERS_TO_SIMULATE + 1):

    # TODO 1: Calculate Inter-Arrival Time using exponential distribution
    # Formula: -math.log(random.random()) * MEAN_INTERARRIVAL_TIME
    interarrival_time = # YOUR CODE HERE

    # TODO 2: Calculate this customer's arrival time
    # Formula: time_of_previous_arrival + interarrival_time
    arrival_time = # YOUR CODE HERE

    # TODO 3: Calculate service time using uniform distribution
    # Formula: random.uniform(MIN_SERVICE_TIME, MAX_SERVICE_TIME)
    service_time = # YOUR CODE HERE

    # TODO 4: Calculate when service begins for this customer
    # Hint: Service begins at the LATER of arrival_time or time_server_is_free
    # Use the max() function
    time_service_begins = # YOUR CODE HERE

    # TODO 5: Calculate wait time in queue
    # Formula: time_service_begins - arrival_time
    wait_in_queue = # YOUR CODE HERE

    # TODO 6: Calculate when service ends
    # Formula: time_service_begins + service_time
    time_service_ends = # YOUR CODE HERE

    # TODO 7: Calculate total time in system
    # Formula: time_service_ends - arrival_time
    time_in_system = # YOUR CODE HERE

    # TODO 8: Calculate server idle time before this customer
    # Formula: time_service_begins - time_server_is_free
    server_idle_time = # YOUR CODE HERE

    # TODO 9: Store the results in the appropriate lists
    # Use .append() method
    # YOUR CODE HERE (3 lines)

    # TODO 10: Update the state variables for the next customer
    # time_of_previous_arrival = ?
    # time_server_is_free = ?
    # YOUR CODE HERE (2 lines)

# --- Calculate and Display Output KPIs ---

# TODO 11: Calculate average wait time
# Formula: sum(wait_times) / len(wait_times)
avg_wait_time = # YOUR CODE HERE

# TODO 12: Calculate probability of waiting
# Count how many customers had wait_time > 0, divide by total customers
customers_who_waited = len([w for w in wait_times if w > 0])
prob_wait = # YOUR CODE HERE

# TODO 13: Calculate server utilization
# Total simulation time = when last customer leaves (time_server_is_free)
# Total idle time = sum of all idle periods
# Total busy time = total simulation time - total idle time
# Utilization = busy time / total simulation time
total_simulation_time = # YOUR CODE HERE
total_idle_time = # YOUR CODE HERE
total_busy_time = # YOUR CODE HERE
server_utilization = # YOUR CODE HERE

# TODO 14: Calculate other metrics
avg_time_in_system = # YOUR CODE HERE
max_wait_time = # YOUR CODE HERE

# TODO 15: Print the results
print("\n" + "="*50)
print("           SIMULATION RESULTS")
print("="*50)
# Add your print statements here to display the metrics
# Use f-strings for formatted output: print(f"Average Wait Time: {avg_wait_time:.2f} minutes")
# YOUR CODE HERE
