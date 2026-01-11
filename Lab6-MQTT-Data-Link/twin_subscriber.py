"""
Lab 6: MQTT Data Link - Digital Twin Subscriber
================================================

Simulates a Digital Twin application that subscribes to sensor data via MQTT.

This script demonstrates the "Subscriber" side of the Publish/Subscribe pattern,
receiving real-time data from physical assets (or simulated sensors).

Prerequisites:
    - paho-mqtt library: pip install paho-mqtt
    - Running MQTT broker (e.g., Mosquitto)
      Install: apt-get install mosquitto mosquitto-clients
      Start: mosquitto -v
    - Running sensor_publisher.py (the data source)

MQTT Concepts Demonstrated:
    - Subscribing to topics
    - Callback-driven message handling
    - JSON deserialization
    - Topic wildcards (optional)
    - Connection state management
    - Persistent listening loop

Digital Twin Concepts:
    - Real-time state synchronization
    - Historical data buffering
    - Statistical analysis of sensor streams
    - Anomaly detection potential
    - Time-series data management

Usage:
    1. Start Mosquitto broker: mosquitto -v
    2. Start sensor_publisher.py: python sensor_publisher.py
    3. Start this subscriber: python twin_subscriber.py
    4. Observe received messages and twin state updates
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime
from collections import deque
import statistics

# ========================================================================================
# CONFIGURATION
# ========================================================================================

# MQTT Broker Configuration
BROKER_ADDRESS = "localhost"  # Local MQTT broker
PORT = 1883                   # Default MQTT port

# MQTT Topic Configuration
# Subscribe to the same topic the sensor publishes to
TOPIC = "digital_twin/lab/sensor/temperature"

# Alternative: Use wildcards to subscribe to multiple topics
# TOPIC = "digital_twin/lab/sensor/#"  # All sensors
# TOPIC = "digital_twin/#"             # All digital twin data

# Digital Twin Configuration
TWIN_ID = "COFFEE_SHOP_TWIN_001"  # Unique identifier for this twin
BUFFER_SIZE = 50                   # Number of recent readings to store
ANOMALY_THRESHOLD = 3.0            # Std deviations for anomaly detection


# ========================================================================================
# DIGITAL TWIN STATE
# ========================================================================================

class DigitalTwinState:
    """
    Represents the internal state of the Digital Twin.

    In a real Digital Twin, this would include:
    - Physical state variables (temperature, position, etc.)
    - Model parameters
    - Prediction/simulation results
    - Control outputs

    For this lab, we focus on sensor data aggregation and analysis.
    """

    def __init__(self, buffer_size=BUFFER_SIZE):
        """
        Initialize the Digital Twin state.

        Args:
            buffer_size: Maximum number of readings to retain
        """
        # Circular buffer for recent temperature readings
        # deque provides O(1) append and automatic size limiting
        self.temperature_buffer = deque(maxlen=buffer_size)
        self.timestamp_buffer = deque(maxlen=buffer_size)

        # Current state
        self.current_temperature = None
        self.last_update_time = None
        self.sensor_id = None

        # Statistics
        self.message_count = 0
        self.anomaly_count = 0
        self.first_message_time = None

        # Metadata from sensor
        self.sensor_metadata = {}

    def update(self, sensor_data):
        """
        Update twin state with new sensor reading.

        This is where the "Digital Twin" synchronizes with the physical asset.

        Args:
            sensor_data: Dictionary containing sensor reading
        """
        # Extract data from sensor payload
        temperature = sensor_data.get("value")
        timestamp_str = sensor_data.get("timestamp_utc")
        sensor_id = sensor_data.get("sensor_id")
        unit = sensor_data.get("unit")
        metadata = sensor_data.get("metadata", {})

        # Update current state
        self.current_temperature = temperature
        self.sensor_id = sensor_id
        self.sensor_metadata = metadata

        # Parse timestamp
        try:
            # Remove 'Z' suffix and parse ISO 8601 format
            timestamp = datetime.fromisoformat(timestamp_str.rstrip('Z'))
            self.last_update_time = timestamp
        except:
            self.last_update_time = datetime.utcnow()

        # Add to historical buffer
        self.temperature_buffer.append(temperature)
        self.timestamp_buffer.append(self.last_update_time)

        # Update statistics
        self.message_count += 1
        if self.first_message_time is None:
            self.first_message_time = self.last_update_time

        # Check for anomalies
        if self.is_anomaly(temperature):
            self.anomaly_count += 1
            return True  # Signal anomaly detected

        return False  # Normal reading

    def is_anomaly(self, value):
        """
        Detect anomalies using statistical method (Z-score).

        An anomaly is defined as a value that deviates more than
        ANOMALY_THRESHOLD standard deviations from the mean.

        Args:
            value: Temperature value to check

        Returns:
            bool: True if anomaly detected
        """
        # Need at least 10 samples for meaningful statistics
        if len(self.temperature_buffer) < 10:
            return False

        try:
            mean = statistics.mean(self.temperature_buffer)
            stdev = statistics.stdev(self.temperature_buffer)

            # Avoid division by zero
            if stdev < 0.01:
                return False

            # Calculate Z-score
            z_score = abs((value - mean) / stdev)

            return z_score > ANOMALY_THRESHOLD

        except statistics.StatisticsError:
            return False

    def get_statistics(self):
        """
        Calculate statistics from buffered data.

        Returns:
            dict: Statistical summary
        """
        if not self.temperature_buffer:
            return {}

        temps = list(self.temperature_buffer)

        stats = {
            "count": len(temps),
            "current": self.current_temperature,
            "mean": round(statistics.mean(temps), 2),
            "min": round(min(temps), 2),
            "max": round(max(temps), 2),
        }

        # Standard deviation requires at least 2 samples
        if len(temps) >= 2:
            stats["stdev"] = round(statistics.stdev(temps), 2)

        return stats

    def get_summary(self):
        """
        Generate a summary of the twin's state.

        Returns:
            str: Formatted summary
        """
        stats = self.get_statistics()

        summary = f"\n{'='*70}\n"
        summary += f"DIGITAL TWIN STATE SUMMARY\n"
        summary += f"{'='*70}\n"
        summary += f"Twin ID: {TWIN_ID}\n"
        summary += f"Sensor ID: {self.sensor_id}\n"
        summary += f"Messages Received: {self.message_count}\n"
        summary += f"Anomalies Detected: {self.anomaly_count}\n"

        if self.first_message_time and self.last_update_time:
            duration = (self.last_update_time - self.first_message_time).total_seconds()
            summary += f"Session Duration: {duration:.1f} seconds\n"

        summary += f"\nTemperature Statistics:\n"
        summary += f"  Current: {stats.get('current', 'N/A')}°C\n"
        summary += f"  Mean:    {stats.get('mean', 'N/A')}°C\n"
        summary += f"  Min:     {stats.get('min', 'N/A')}°C\n"
        summary += f"  Max:     {stats.get('max', 'N/A')}°C\n"
        summary += f"  StdDev:  {stats.get('stdev', 'N/A')}°C\n"

        if self.sensor_metadata:
            summary += f"\nSensor Metadata:\n"
            for key, value in self.sensor_metadata.items():
                summary += f"  {key}: {value}\n"

        summary += f"{'='*70}\n"

        return summary


# ========================================================================================
# MQTT CLIENT SETUP
# ========================================================================================

# Create Digital Twin state instance
twin_state = DigitalTwinState()

# Create MQTT client instance
# Using callback_api_version for paho-mqtt v2.x compatibility
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "TwinSubscriber")


def on_connect(client, userdata, flags, rc):
    """
    Callback when client connects to broker.

    This is where we subscribe to topics. Subscribing in on_connect
    ensures that subscriptions are renewed if the connection is lost
    and re-established.

    Args:
        client: MQTT client instance
        userdata: User-defined data
        flags: Response flags from broker
        rc: Connection result code (0 = success)
    """
    if rc == 0:
        print(f"\n{'='*70}")
        print(f"MQTT DIGITAL TWIN SUBSCRIBER")
        print(f"{'='*70}")
        print(f"✓ Connected to MQTT broker at {BROKER_ADDRESS}:{PORT}")
        print(f"  Twin ID: {TWIN_ID}")
        print(f"  Subscribing to topic: {TOPIC}")
        print(f"{'='*70}\n")
        print("Waiting for sensor data... (Press Ctrl+C to stop)\n")

        # Subscribe to the topic
        # QoS (Quality of Service):
        #   0 = At most once (may lose messages)
        #   1 = At least once (may get duplicates)
        #   2 = Exactly once (guaranteed single delivery)
        client.subscribe(TOPIC, qos=0)

    else:
        print(f"✗ Connection failed with code {rc}")
        connection_errors = {
            1: "Incorrect protocol version",
            2: "Invalid client identifier",
            3: "Server unavailable",
            4: "Bad username or password",
            5: "Not authorized"
        }
        error_msg = connection_errors.get(rc, "Unknown error")
        print(f"  Error: {error_msg}")


def on_message(client, userdata, msg):
    """
    Callback when a message is received.

    This is the heart of the Digital Twin - processing incoming sensor data.

    Args:
        client: MQTT client instance
        userdata: User-defined data
        msg: MQTT message object (has .topic and .payload attributes)
    """
    try:
        # Decode payload from bytes to string
        payload_str = msg.payload.decode('utf-8')

        # Parse JSON
        sensor_data = json.loads(payload_str)

        # Update Digital Twin state
        is_anomaly = twin_state.update(sensor_data)

        # Display received message
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Message #{twin_state.message_count}")
        print(f"  Topic: {msg.topic}")
        print(f"  Sensor: {sensor_data.get('sensor_id', 'Unknown')}")
        print(f"  Temperature: {sensor_data.get('value')}°{sensor_data.get('unit', 'C')}")
        print(f"  Timestamp: {sensor_data.get('timestamp_utc', 'N/A')}")

        # Flag anomalies
        if is_anomaly:
            print(f"  ⚠ ANOMALY DETECTED! (Total: {twin_state.anomaly_count})")

        # Show running statistics every 10 messages
        if twin_state.message_count % 10 == 0:
            stats = twin_state.get_statistics()
            print(f"\n  📊 Statistics (last {stats['count']} readings):")
            print(f"     Mean: {stats['mean']}°C  |  Range: [{stats['min']}, {stats['max']}]°C", end="")
            if 'stdev' in stats:
                print(f"  |  σ: {stats['stdev']}°C")
            else:
                print()

        print()  # Blank line for readability

    except json.JSONDecodeError as e:
        # Handle malformed JSON
        print(f"✗ Error: Invalid JSON received")
        print(f"  Payload: {msg.payload}")
        print(f"  Error: {e}\n")

    except Exception as e:
        # Handle other unexpected errors
        print(f"✗ Unexpected error processing message: {e}\n")


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
    Callback when subscription is confirmed (optional).

    Args:
        client: MQTT client instance
        userdata: User-defined data
        mid: Message ID
        granted_qos: QoS level granted by broker
    """
    print(f"✓ Subscription confirmed (QoS: {granted_qos[0]})\n")


def on_disconnect(client, userdata, rc):
    """
    Callback when client disconnects from broker.

    Args:
        client: MQTT client instance
        userdata: User-defined data
        rc: Disconnection result code (0 = clean disconnect)
    """
    if rc != 0:
        print(f"\n⚠ Unexpected disconnect (code {rc})")
        print("  Attempting to reconnect...")


# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_disconnect = on_disconnect


# ========================================================================================
# MAIN LISTENING LOOP
# ========================================================================================

def main():
    """
    Main function: Connect to broker and listen for messages.
    """
    # Connect to MQTT broker
    try:
        client.connect(BROKER_ADDRESS, PORT)

    except Exception as e:
        print(f"\n✗ Failed to connect to broker: {e}")
        print(f"  Is Mosquitto running? Try: mosquitto -v")
        return

    # Start listening loop
    # loop_forever() blocks and processes network traffic, dispatches callbacks
    # This is different from the publisher which used loop_start() + manual loop
    try:
        # This will run until Ctrl+C or disconnect
        client.loop_forever()

    except KeyboardInterrupt:
        # Clean shutdown on Ctrl+C
        print("\n\nShutting down Digital Twin subscriber...")

        # Display final summary
        print(twin_state.get_summary())

        # Disconnect cleanly
        client.disconnect()

        print("✓ Disconnected from broker. Goodbye!\n")


# ========================================================================================
# SCRIPT EXECUTION
# ========================================================================================

if __name__ == "__main__":
    main()
