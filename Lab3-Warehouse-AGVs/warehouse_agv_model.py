"""
Lab 3: Twinning a Warehouse with AGVs - Agent-Based Modeling
============================================================

This script implements a complete agent-based model of a warehouse populated by
Autonomous Guided Vehicles (AGVs) using the Mesa framework.

Key ABM Concepts Demonstrated:
    - Agent State and Rules: AGV state machines with behavior rules
    - Agent-Environment Interaction: Pathfinding through warehouse layout
    - Agent-Agent Interaction: Collision avoidance and sensing
    - Emergence: Traffic congestion patterns that emerge from local rules
    - Spatial Environment: 2D grid representing warehouse floor
    - Instrumentation: Hook methods for Digital Twin integration

Four-Phase Implementation:
    1. Environment and Static Agent Setup
    2. Dynamic AGV Agent with State Machine
    3. Visualization and Emergence Observation
    4. Instrumentation for Twinning

How to Run:
    python warehouse_agv_model.py

Then open your browser to: http://127.0.0.1:8521

What to Observe:
    - Watch AGVs change color based on their state
    - Look for RED AGVs clustering near drop-off points (emergent traffic jams!)
    - Notice how collision avoidance creates bottlenecks
    - Observe battery management and charging behavior
"""

import mesa
import random
from typing import List, Tuple, Optional, Dict
from queue import PriorityQueue

# ========================================================================================
# PHASE 1: A* PATHFINDING ALGORITHM
# ========================================================================================

def heuristic(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """
    Manhattan distance heuristic for A* pathfinding.

    Args:
        pos1: Starting position (x, y)
        pos2: Goal position (x, y)

    Returns:
        Manhattan distance between positions
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def astar(grid: mesa.space.MultiGrid, start: Tuple[int, int], end: Tuple[int, int],
          obstacles: List[type]) -> List[Tuple[int, int]]:
    """
    A* pathfinding algorithm to navigate around obstacles in the warehouse.

    This is crucial for Agent-Environment Interaction: AGVs must intelligently
    navigate around walls and shelves to reach their destinations.

    Args:
        grid: The Mesa MultiGrid representing the warehouse
        start: Starting position (x, y)
        end: Goal position (x, y)
        obstacles: List of agent types to treat as non-navigable

    Returns:
        List of (x, y) coordinates representing the path, or empty list if no path exists
    """
    # Priority queue for frontier nodes: (f_score, counter, position, path)
    frontier = PriorityQueue()
    frontier.put((0, 0, start, [start]))
    visited = set()
    counter = 0  # Tiebreaker for priority queue

    while not frontier.empty():
        f_score, _, current, path = frontier.get()

        # Goal reached!
        if current == end:
            return path

        if current in visited:
            continue
        visited.add(current)

        # Explore neighbors (4-directional movement)
        x, y = current
        neighbors = [
            (x + 1, y), (x - 1, y),
            (x, y + 1), (x, y - 1)
        ]

        for next_pos in neighbors:
            # Check if neighbor is within grid bounds
            if not (0 <= next_pos[0] < grid.width and 0 <= next_pos[1] < grid.height):
                continue

            # Check if neighbor is navigable (not an obstacle)
            cell_contents = grid.get_cell_list_contents([next_pos])
            is_obstacle = any(isinstance(agent, tuple(obstacles)) for agent in cell_contents)

            if is_obstacle or next_pos in visited:
                continue

            # Calculate scores
            g_score = len(path)  # Cost from start
            h_score = heuristic(next_pos, end)  # Estimated cost to goal
            f_score = g_score + h_score

            # Add to frontier
            counter += 1
            new_path = path + [next_pos]
            frontier.put((f_score, counter, next_pos, new_path))

    # No path found
    return []


# ========================================================================================
# PHASE 1: STATIC AGENTS - ENVIRONMENT FEATURES
# ========================================================================================

class WallAgent(mesa.Agent):
    """
    Static agent representing a wall.

    Walls are non-navigable obstacles that AGVs must path around.
    These agents do not have behavior (no step method) - they are
    purely environmental markers.
    """
    def __init__(self, model: mesa.Model):
        super().__init__(model)


class ShelfAgent(mesa.Agent):
    """
    Static agent representing a storage shelf.

    Shelves are obstacles that define the warehouse layout and
    create narrow pathways where congestion can emerge.
    """
    def __init__(self, model: mesa.Model):
        super().__init__(model)


class ChargingStationAgent(mesa.Agent):
    """
    Static agent representing a charging station.

    AGVs navigate to these locations when battery is low.
    Multiple AGVs may need to queue for charging, creating
    another source of emergent congestion.
    """
    def __init__(self, model: mesa.Model):
        super().__init__(model)


class DropoffPointAgent(mesa.Agent):
    """
    Static agent representing a package drop-off point.

    These are high-traffic destinations where emergent
    traffic jams are most likely to occur.
    """
    def __init__(self, model: mesa.Model):
        super().__init__(model)


# ========================================================================================
# PHASE 2: DYNAMIC AGV AGENT WITH STATE MACHINE
# ========================================================================================

class AGVAgent(mesa.Agent):
    """
    Dynamic agent representing an Autonomous Guided Vehicle.

    This agent demonstrates the core ABM concept of autonomous entities with:
    - Internal State: battery level, current task, position, state machine
    - Rules & Behavior: State-dependent actions defined in step()
    - Sensing: Ability to detect other AGVs for collision avoidance
    - Goal-Directed: Uses pathfinding to navigate to destinations

    State Machine States:
        - IDLE: Waiting for a task assignment
        - MOVING_TO_PICKUP: En route to pick up a package
        - DELIVERING: En route to drop off a package
        - CHARGING: At a charging station, replenishing battery
        - WAITING: Blocked by another AGV (emergent behavior!)
    """

    def __init__(self, model: mesa.Model, pos: Tuple[int, int]):
        """
        Initialize an AGV agent.

        Args:
            model: Reference to the WarehouseModel
            pos: Starting position (x, y)

        Note: unique_id is automatically assigned by Mesa 3.x
        """
        super().__init__(model)

        # Physical state
        self.pos = pos
        self.battery_level = 100.0  # Percentage

        # Task and navigation state
        self.state = "IDLE"
        self.task = None  # Will be a dict: {'pickup': (x,y), 'dropoff': (x,y)}
        self.path = []  # List of positions to follow

        # State tracking for visualization and analysis
        self.steps_waiting = 0  # Track how long blocked (for emergence analysis)

        # Configuration
        self.battery_drain_rate = 0.5  # % per move
        self.battery_charge_rate = 5.0  # % per step at station
        self.low_battery_threshold = 20.0

    # ====================================================================================
    # PHASE 2: CORE BEHAVIOR - STATE MACHINE
    # ====================================================================================

    def step(self):
        """
        Execute one step of the AGV's behavior (called each simulation tick).

        This method implements the AGV's state machine, demonstrating how
        complex emergent behaviors arise from simple local rules.
        """
        # RULE 1: Battery Management (highest priority)
        # If battery is critically low and not already charging, interrupt current task
        if self.battery_level < self.low_battery_threshold and self.state != "CHARGING":
            self._start_charging()
            return

        # RULE 2: State-dependent behavior
        if self.state == "IDLE":
            self._handle_idle_state()

        elif self.state == "MOVING_TO_PICKUP":
            self._follow_path()
            # Check if reached pickup location
            if self.path == [] and self.task is not None:
                self.state = "DELIVERING"
                self._calculate_path_to(self.task['dropoff'])

        elif self.state == "DELIVERING":
            self._follow_path()
            # Check if reached dropoff location
            if self.path == []:
                self._complete_task()

        elif self.state == "CHARGING":
            self._charge_battery()

    def _handle_idle_state(self):
        """
        Behavior when AGV is idle: request a new task from the warehouse.
        """
        task = self.model.assign_task_to_agv(self)
        if task is not None:
            self.task = task
            self.state = "MOVING_TO_PICKUP"
            self._calculate_path_to(task['pickup'])

    def _follow_path(self):
        """
        Follow the planned path, implementing collision avoidance.

        This is where EMERGENCE happens! Each AGV follows simple rules:
        1. Try to move to next position on path
        2. If blocked by another AGV, wait

        From these simple rules, complex traffic patterns emerge:
        - Congestion at bottlenecks
        - Deadlocks in narrow passages
        - Queue formation at popular destinations
        """
        if not self.path:
            return

        next_pos = self.path[0]

        # AGENT-AGENT INTERACTION: Collision Avoidance
        # Check if next position is occupied by another AGV
        cell_contents = self.model.grid.get_cell_list_contents([next_pos])
        other_agvs = [agent for agent in cell_contents if isinstance(agent, AGVAgent)]

        if other_agvs:
            # EMERGENT BEHAVIOR: Waiting/blocking
            self.state = "WAITING"
            self.steps_waiting += 1
            return  # Don't move this step - creates congestion!

        # Path is clear - move!
        if self.state == "WAITING":
            self.state = "MOVING_TO_PICKUP" if self.task and 'pickup' in self.task else "DELIVERING"

        self.model.grid.move_agent(self, next_pos)
        self.pos = next_pos
        self.path.pop(0)  # Remove completed step

        # Deplete battery when moving
        self.battery_level = max(0, self.battery_level - self.battery_drain_rate)
        self.steps_waiting = 0  # Reset waiting counter

    def _start_charging(self):
        """
        Interrupt current task and navigate to nearest charging station.
        """
        charging_stations = [agent for agent in self.model.agents
                           if isinstance(agent, ChargingStationAgent)]

        if not charging_stations:
            return  # No charging stations available!

        # Find nearest charging station
        nearest_station = min(charging_stations,
                            key=lambda s: heuristic(self.pos, s.pos))

        self.state = "CHARGING"
        self._calculate_path_to(nearest_station.pos)

    def _charge_battery(self):
        """
        Charge battery when at a charging station.
        """
        # Check if actually at a charging station
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        at_station = any(isinstance(agent, ChargingStationAgent) for agent in cell_contents)

        if at_station:
            # Charge battery
            self.battery_level = min(100.0, self.battery_level + self.battery_charge_rate)

            # If fully charged, return to idle
            if self.battery_level >= 100.0:
                self.state = "IDLE"
                self.task = None  # Clear any interrupted task
        else:
            # Not at station yet, keep moving
            self._follow_path()

    def _complete_task(self):
        """
        Complete current delivery task and return to idle.
        """
        self.task = None
        self.state = "IDLE"

    def _calculate_path_to(self, destination: Tuple[int, int]):
        """
        Calculate path to destination using A* algorithm.

        Args:
            destination: Target position (x, y)
        """
        obstacles = [WallAgent, ShelfAgent]
        self.path = astar(self.model.grid, self.pos, destination, obstacles)

        if not self.path:
            # No path found - return to idle
            self.state = "IDLE"
            self.task = None

    # ====================================================================================
    # PHASE 4: INSTRUMENTATION FOR DIGITAL TWIN
    # ====================================================================================

    def override_position(self, new_pos: Tuple[int, int]):
        """
        DIGITAL TWIN HOOK: Override agent position based on real-world data.

        In a real Digital Twin system, this method would be called when data
        arrives from the physical AGV's location sensors. This ensures the
        simulation state matches the real-world state.

        Args:
            new_pos: New position from real-world sensor data
        """
        self.model.grid.move_agent(self, new_pos)
        self.pos = new_pos
        print(f"[TWIN HOOK] AGV {self.unique_id} position overridden to {new_pos}")

    def assign_external_task(self, task: Dict):
        """
        DIGITAL TWIN HOOK: Assign task from external warehouse management system.

        In a real Digital Twin, this would be called when the physical warehouse's
        WMS assigns a new task. The simulation immediately reflects this assignment.

        Args:
            task: Task dictionary with 'pickup' and 'dropoff' positions
        """
        # Interrupt current task (unless critically low battery)
        if self.battery_level > 10.0:
            self.task = task
            self.state = "MOVING_TO_PICKUP"
            self._calculate_path_to(task['pickup'])
            print(f"[TWIN HOOK] AGV {self.unique_id} assigned external task: {task}")


# ========================================================================================
# PHASE 1: WAREHOUSE MODEL - ENVIRONMENT AND SCHEDULER
# ========================================================================================

class WarehouseModel(mesa.Model):
    """
    Main model class representing the warehouse environment.

    This class manages:
    - Spatial environment (MultiGrid)
    - Agent scheduling (RandomActivation)
    - Task generation and assignment
    - Warehouse layout initialization
    """

    def __init__(self, width: int = 30, height: int = 30, num_agvs: int = 15):
        """
        Initialize the warehouse model.

        Args:
            width: Grid width
            height: Grid height
            num_agvs: Number of AGV agents to create
        """
        super().__init__()

        # Spatial environment: MultiGrid allows multiple agents per cell
        self.grid = mesa.space.MultiGrid(width, height, torus=False)

        # Task management
        self.available_tasks = []
        self.completed_tasks = 0

        # Build the warehouse layout
        self._create_warehouse_layout()

        # Create AGV agents
        self._create_agv_fleet(num_agvs)

        # Generate initial tasks
        self._generate_tasks(30)  # Start with 30 tasks in the queue

    def _create_warehouse_layout(self):
        """
        Create the warehouse layout using a text-based map.

        Legend:
            '#' = Wall
            'S' = Shelf
            'C' = Charging Station
            'D' = Dropoff Point
            ' ' = Open space
        """
        # Define warehouse layout (30x30)
        layout = [
            "##############################",
            "#                            #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#                          D #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#                          D #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#                          D #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#                            #",
            "#            C  C  C         #",
            "#                            #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#                          D #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#                          D #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#                          D #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#  SSSS  SSSS  SSSS  SSSS    #",
            "#                            #",
            "#                            #",
            "##############################",
        ]

        # Place static agents based on layout
        for y, row in enumerate(layout):
            for x, cell in enumerate(row):
                if cell == '#':
                    wall = WallAgent(self)
                    self.grid.place_agent(wall, (x, y))
                elif cell == 'S':
                    shelf = ShelfAgent(self)
                    self.grid.place_agent(shelf, (x, y))
                elif cell == 'C':
                    station = ChargingStationAgent(self)
                    self.grid.place_agent(station, (x, y))
                elif cell == 'D':
                    dropoff = DropoffPointAgent(self)
                    self.grid.place_agent(dropoff, (x, y))

    def _create_agv_fleet(self, num_agvs: int):
        """
        Create the fleet of AGV agents.

        Args:
            num_agvs: Number of AGVs to create
        """
        # Find all open spaces for AGV starting positions
        open_spaces = []
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell_contents = self.grid.get_cell_list_contents([(x, y)])
                # Cell is open if it has no agents or only has dropoff/charging
                is_open = not any(isinstance(agent, (WallAgent, ShelfAgent, AGVAgent))
                                for agent in cell_contents)
                if is_open:
                    open_spaces.append((x, y))

        # Create AGVs at random open positions
        for i in range(num_agvs):
            if open_spaces:
                pos = random.choice(open_spaces)
                open_spaces.remove(pos)  # Don't place multiple AGVs at same spot initially

                agv = AGVAgent(self, pos)
                self.grid.place_agent(agv, pos)

    def _generate_tasks(self, num_tasks: int):
        """
        Generate random delivery tasks.

        Args:
            num_tasks: Number of tasks to generate
        """
        # Find all shelf positions (pickup points)
        shelf_positions = [agent.pos for agent in self.agents
                          if isinstance(agent, ShelfAgent)]

        # Find all dropoff positions
        dropoff_positions = [agent.pos for agent in self.agents
                            if isinstance(agent, DropoffPointAgent)]

        if not shelf_positions or not dropoff_positions:
            return

        # Generate tasks
        for _ in range(num_tasks):
            task = {
                'pickup': random.choice(shelf_positions),
                'dropoff': random.choice(dropoff_positions)
            }
            self.available_tasks.append(task)

    def assign_task_to_agv(self, agv: AGVAgent) -> Optional[Dict]:
        """
        Assign a task to an AGV agent.

        Args:
            agv: The AGV requesting a task

        Returns:
            Task dictionary or None if no tasks available
        """
        if self.available_tasks:
            task = self.available_tasks.pop(0)

            # Generate new tasks to keep the queue full
            if len(self.available_tasks) < 10:
                self._generate_tasks(5)

            return task
        return None

    def step(self):
        """
        Execute one step of the model (all agents act once).

        In Mesa 3.x, we use shuffle_do() to execute agent methods in random order.
        This prevents artifacts from fixed execution order, equivalent to RandomActivation.
        """
        # Only call step on AGV agents (static agents don't have step methods)
        self.agents.select(lambda a: isinstance(a, AGVAgent)).shuffle_do("step")


# ========================================================================================
# PHASE 3: VISUALIZATION - MESA SERVER SETUP
# ========================================================================================

def agent_portrayal(agent):
    """
    Define how agents are visualized in the Mesa grid.

    This function is critical for observing emergence:
    - AGV colors change based on state
    - Watch for clusters of RED (waiting) AGVs = emergent traffic jams!
    - YELLOW AGVs near charging stations = battery management behavior
    - BLUE AGVs = active deliveries

    Args:
        agent: The agent to visualize

    Returns:
        Dictionary defining the agent's visual representation
    """
    if isinstance(agent, AGVAgent):
        # AGV visualization - COLOR REPRESENTS STATE (key for emergence observation!)
        color_map = {
            "IDLE": "#00FF00",        # Green - waiting for task
            "MOVING_TO_PICKUP": "#00BFFF",  # Light blue - going to pickup
            "DELIVERING": "#0000FF",   # Blue - delivering package
            "CHARGING": "#FFFF00",     # Yellow - charging battery
            "WAITING": "#FF0000",      # RED - blocked/congested (EMERGENCE!)
        }

        portrayal = {
            "Shape": "circle",
            "Color": color_map.get(agent.state, "#808080"),
            "Filled": "true",
            "Layer": 2,
            "r": 0.8,
            "text": f"{int(agent.battery_level)}%",
            "text_color": "black"
        }
        return portrayal

    elif isinstance(agent, WallAgent):
        return {
            "Shape": "rect",
            "Color": "#000000",  # Black
            "Filled": "true",
            "Layer": 0,
            "w": 1,
            "h": 1
        }

    elif isinstance(agent, ShelfAgent):
        return {
            "Shape": "rect",
            "Color": "#8B4513",  # Brown
            "Filled": "true",
            "Layer": 0,
            "w": 1,
            "h": 1
        }

    elif isinstance(agent, ChargingStationAgent):
        return {
            "Shape": "rect",
            "Color": "#FFD700",  # Gold
            "Filled": "true",
            "Layer": 1,
            "w": 1,
            "h": 1,
            "text": "⚡",
            "text_color": "black"
        }

    elif isinstance(agent, DropoffPointAgent):
        return {
            "Shape": "rect",
            "Color": "#FF69B4",  # Pink
            "Filled": "true",
            "Layer": 1,
            "w": 1,
            "h": 1,
            "text": "D",
            "text_color": "white"
        }


# ========================================================================================
# MAIN EXECUTION - LAUNCH VISUALIZATION SERVER
# ========================================================================================

def main():
    """
    Launch the Mesa visualization server.

    INSTRUCTIONS FOR STUDENTS:
    ==========================
    1. Run this script: python warehouse_agv_model.py
    2. Open your browser to: http://127.0.0.1:8521
    3. Click "Start" to begin the simulation
    4. Use "Step" to advance one tick at a time, or let it run continuously

    WHAT TO OBSERVE (EMERGENCE!):
    =============================
    - Watch for RED AGVs (state = WAITING) clustering near dropoff points (pink 'D')
      This is EMERGENT CONGESTION that arises from simple collision avoidance rules!

    - Notice how AGVs sometimes block each other in narrow passages between shelves
      This creates temporary gridlock - another emergent phenomenon

    - Observe YELLOW AGVs (CHARGING) gathering at gold charging stations
      When multiple AGVs need charging simultaneously, queues form naturally

    - The overall traffic patterns are NOT programmed - they EMERGE from:
      1. Each AGV following its own simple rules
      2. AGVs sensing and avoiding each other
      3. The spatial constraints of the warehouse layout

    This is the essence of Agent-Based Modeling: complex system behavior
    emerging from simple individual agent rules!

    DIGITAL TWIN HOOKS:
    ===================
    The AGVAgent class includes override_position() and assign_external_task()
    methods. These are "hooks" for Digital Twin integration. In a real system,
    data from physical AGVs would call these methods to synchronize the
    simulation with reality.
    """
    print("\n" + "="*80)
    print("LAB 3: WAREHOUSE AGV AGENT-BASED MODEL")
    print("="*80)
    print("\nStarting Mesa visualization server...")
    print("\nOpen your browser to: http://127.0.0.1:8521")
    print("\nLook for:")
    print("  - RED AGVs = Blocked/waiting (EMERGENT traffic congestion!)")
    print("  - BLUE AGVs = Actively delivering")
    print("  - YELLOW AGVs = Charging battery")
    print("  - GREEN AGVs = Idle, waiting for tasks")
    print("\nWatch how complex traffic patterns EMERGE from simple agent rules!")
    print("="*80 + "\n")

    # Create the visualization grid
    grid = mesa.visualization.CanvasGrid(
        agent_portrayal,
        30, 30,  # Grid dimensions
        600, 600  # Canvas size in pixels
    )

    # Create the visualization server
    server = mesa.visualization.ModularServer(
        WarehouseModel,
        [grid],
        "Warehouse AGV Digital Twin",
        {
            "width": 30,
            "height": 30,
            "num_agvs": mesa.visualization.Slider(
                "Number of AGVs",
                15,  # Default
                5,   # Min
                25,  # Max
                1    # Step
            )
        }
    )

    server.port = 8521
    server.launch()


if __name__ == "__main__":
    main()
