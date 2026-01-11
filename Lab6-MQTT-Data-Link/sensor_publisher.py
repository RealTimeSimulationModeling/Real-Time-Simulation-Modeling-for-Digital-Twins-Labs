"""
Lab 6: MQTT Data Link - Sensor Publisher
=========================================

Simulates a temperature sensor that publishes its readings to an MQTT topic.

This script demonstrates the "Publisher" side of the Publish/Subscribe pattern,
which is fundamental to IoT and Digital Twin architectures.

Prerequisites:
    - paho-mqtt library: pip install paho-mqtt
    - Running MQTT broker (e.g., Mosquitto)
      Install: apt-get install mosquitto mosquitto-clients
      Start: mosquitto -v

MQTT Concepts Demonstrated:
    - Publishing to a topic
    - JSON serialization for structured data
    - UTC timestamps for time synchronization
    - Periodic data transmission
    - Clean disconnect handling

Usage:
    1. Start Mosquitto broker: mosquitto -v
    2. Start this publisher: python sensor_publisher.py
    3. Observe published messages in console
    4. Start twin_subscriber.py in another terminal to receive data
"""

import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime

# ========================================================================================
# CONFIGURATION
# ========================================================================================

# MQTT Broker Configuration
BROKER_ADDRESS = "localhost"  # Local MQTT broker
PORT = 1883                   # Default MQTT port (unencrypted)
                              # Port 8883 is for MQTT over TLS/SSL

# MQTT Topic Configuration
# Topic naming convention: domain/application/source/measurement_type
# This hierarchical structure enables flexible subscription patterns
TOPIC = "digital_twin/lab/sensor/temperature"

# Sensor Configuration
SENSOR_ID = "TEMP_SENSOR_001"  # Unique identifier for this sensor
PUBLISH_INTERVAL = 2           # Seconds between readings
UNIT = "Celsius"              # Temperature unit

# Simulation Parameters (for realistic data generation)
BASE_TEMPERATURE = 22.0        # Base temperature (°C)
TEMPERATURE_VARIANCE = 3.0     # Random variation (±°C)
DRIFT_RATE = 0.1              # Slow drift to simulate environment changes


# ========================================================================================
# MQTT CLIENT SETUP
# ========================================================================================

# Create MQTT client instance
# Client ID must be unique for each client connected to the broker
# Using callback_api_version for paho-mqtt v2.x compatibility
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "SensorPublisher")

# Optional: Set up callbacks for connection events
def on_connect(client, userdata, flags, rc):
    """
    Callback when client connects to broker.

    Args:
        client: MQTT client instance
        userdata: User-defined data
        flags: Response flags from broker
        rc: Connection result code (0 = success)
    """
    if rc == 0:
        print(f"✓ Connected to MQTT broker at {BROKER_ADDRESS}:{PORT}")
        print(f"  Publishing to topic: {TOPIC}")
        print(f"  Sensor ID: {SENSOR_ID}")
        print(f"  Publish interval: {PUBLISH_INTERVAL} seconds")
        print("-" * 70)
    else:
        print(f"✗ Connection failed with code {rc}")

def on_publish(client, userdata, mid):
    """
    Callback when message is published (optional, for QoS > 0).

    Args:
        client: MQTT client instance
        userdata: User-defined data
        mid: Message ID
    """
    pass  # We'll handle logging in the main loop

# Assign callbacks
client.on_connect = on_connect
client.on_publish = on_publish


# ========================================================================================
# DATA GENERATION
# ========================================================================================

# Initialize temperature with some random offset
current_temperature = BASE_TEMPERATURE + random.uniform(-2, 2)

def generate_temperature_reading():
    """
    Generate a realistic temperature reading with noise and drift.

    This simulates a real sensor that:
    - Has measurement noise (random variation)
    - Experiences environmental drift (gradual changes)
    - Stays within realistic bounds

    Returns:
        float: Temperature in Celsius
    """
    global current_temperature

    # Add random noise (simulates sensor precision limits)
    noise = random.gauss(0, 0.3)  # Gaussian noise, σ = 0.3°C

    # Add slow drift (simulates environmental changes)
    drift = random.uniform(-DRIFT_RATE, DRIFT_RATE)

    # Update current temperature
    current_temperature += drift
    measured_temperature = current_temperature + noise

    # Keep within reasonable bounds (prevent runaway drift)
    current_temperature = max(BASE_TEMPERATURE - TEMPERATURE_VARIANCE,
                             min(BASE_TEMPERATURE + TEMPERATURE_VARIANCE,
                                 current_temperature))

    # Round to realistic sensor precision (0.1°C)
    return round(measured_temperature, 1)


def create_sensor_payload(temperature_value):
    """
    Create a JSON payload for the sensor reading.

    JSON is used for:
    - Human readability
    - Easy parsing in any language
    - Standard format for IoT/Web
    - Self-describing data structure

    Args:
        temperature_value: Temperature reading in Celsius

    Returns:
        str: JSON-formatted payload
    """
    # Create structured data dictionary
    payload = {
        "timestamp_utc": datetime.utcnow().isoformat() + 'Z',  # ISO 8601 format
        "sensor_id": SENSOR_ID,
        "value": temperature_value,
        "unit": UNIT,
        "metadata": {
            "location": "Lab Environment",
            "sensor_type": "Simulated Thermistor",
            "firmware_version": "1.0.0"
        }
    }

    # Serialize to JSON string
    # indent=None for compact transmission (saves bandwidth)
    # For debugging, use indent=2 for pretty-printing
    return json.dumps(payload)


# ========================================================================================
# MAIN PUBLISHING LOOP
# ========================================================================================

def main():
    """
    Main function: Connect to broker and publish sensor readings.
    """
    print("\n" + "="*70)
    print("MQTT SENSOR PUBLISHER - Temperature Sensor Simulation")
    print("="*70)

    # Connect to MQTT broker
    try:
        client.connect(BROKER_ADDRESS, PORT)
        # Start network loop in background thread
        # This handles reconnection, ping/pong, etc.
        client.loop_start()

        # Give connection time to establish
        time.sleep(1)

    except Exception as e:
        print(f"\n✗ Failed to connect to broker: {e}")
        print(f"  Is Mosquitto running? Try: mosquitto -v")
        return

    # Main publishing loop
    try:
        message_count = 0

        print("\nPublishing sensor readings... (Press Ctrl+C to stop)\n")

        while True:
            # Generate temperature reading
            temperature = generate_temperature_reading()

            # Create JSON payload
            json_payload = create_sensor_payload(temperature)

            # Publish to MQTT topic
            # QoS (Quality of Service):
            #   0 = At most once (fire and forget)
            #   1 = At least once (acknowledged delivery)
            #   2 = Exactly once (guaranteed single delivery)
            result = client.publish(TOPIC, json_payload, qos=0)

            # Log successful publish
            message_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")

            print(f"[{timestamp}] Message #{message_count}")
            print(f"  Topic: {TOPIC}")
            print(f"  Temperature: {temperature}°C")
            print(f"  Payload: {json_payload}")

            # Check publish success
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"  Status: ✓ Published successfully")
            else:
                print(f"  Status: ✗ Publish failed (code {result.rc})")

            print()  # Blank line for readability

            # Wait before next reading
            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        # Clean shutdown on Ctrl+C
        print("\n" + "="*70)
        print("Shutting down sensor publisher...")
        print(f"Total messages published: {message_count}")
        print("="*70 + "\n")

        # Disconnect cleanly
        client.loop_stop()
        client.disconnect()

        print("✓ Disconnected from broker. Goodbye!")

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        client.loop_stop()
        client.disconnect()


# ========================================================================================
# SCRIPT EXECUTION
# ========================================================================================

if __name__ == "__main__":
    main()
