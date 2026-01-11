# Lab 6: Building the Data Link with MQTT

## Overview

This lab introduces **MQTT (Message Queuing Telemetry Transport)**, a lightweight messaging protocol that forms the backbone of modern IoT and Digital Twin architectures. You'll build a complete data link between a simulated sensor and a Digital Twin application using the **Publish/Subscribe pattern**.

### Learning Objectives

By the end of this lab, you will understand:

1. **MQTT Protocol Fundamentals**
   - Publish/Subscribe messaging pattern
   - Topics and topic hierarchies
   - Quality of Service (QoS) levels
   - Message brokers and clients

2. **Data Serialization**
   - JSON formatting for structured data
   - ISO 8601 timestamps for time synchronization
   - Metadata inclusion for rich sensor payloads

3. **Digital Twin Communication**
   - Real-time state synchronization
   - Callback-driven event handling
   - Buffering and statistical analysis
   - Anomaly detection techniques

4. **IoT Architecture Patterns**
   - Decoupled producer/consumer design
   - Message broker as central hub
   - Scalability through topic-based routing
   - Loose coupling between components

---

## Why MQTT for Digital Twins?

MQTT is the de facto standard for IoT communication because it:

- **Lightweight**: Minimal overhead, ideal for resource-constrained devices
- **Asynchronous**: Publishers and subscribers don't need to be online simultaneously
- **Scalable**: Brokers can handle millions of messages
- **Reliable**: Multiple QoS levels ensure message delivery
- **Flexible**: Topic hierarchies enable complex routing patterns

For Digital Twins, MQTT enables:
- **Real-time data ingestion** from physical sensors
- **Bidirectional control** (cloud → edge and edge → cloud)
- **Many-to-many communication** (multiple sensors, multiple twins)
- **Edge computing** with local brokers for low-latency control

---

## Architecture

```
┌─────────────────────┐
│  Physical Sensor    │
│  (Simulated)        │
│                     │
│  sensor_publisher.py│
└──────────┬──────────┘
           │ Publishes
           │ Topic: digital_twin/lab/sensor/temperature
           │ Payload: JSON (temp, timestamp, metadata)
           ▼
┌─────────────────────┐
│   MQTT Broker       │
│   (Mosquitto)       │
│                     │
│   Port: 1883        │
└──────────┬──────────┘
           │ Delivers
           │
           ▼
┌─────────────────────┐
│  Digital Twin       │
│                     │
│  twin_subscriber.py │
│  - State sync       │
│  - Statistics       │
│  - Anomaly detection│
└─────────────────────┘
```

### Data Flow

1. **Sensor Publisher** (`sensor_publisher.py`):
   - Simulates a temperature sensor with realistic noise and drift
   - Generates readings every 2 seconds
   - Packages data into JSON payload with timestamp and metadata
   - Publishes to MQTT topic via broker

2. **MQTT Broker** (Mosquitto):
   - Receives published messages
   - Routes messages to all subscribers of matching topics
   - Handles connection management and QoS guarantees
   - Provides decoupling between publishers and subscribers

3. **Digital Twin Subscriber** (`twin_subscriber.py`):
   - Subscribes to sensor topic
   - Receives messages asynchronously via callback
   - Updates internal state representation
   - Calculates statistics (mean, min, max, std dev)
   - Detects anomalies using Z-score method

---

## MQTT Key Concepts

### 1. Publish/Subscribe Pattern

Unlike request/response (HTTP), Pub/Sub is:
- **Asynchronous**: Publisher doesn't wait for subscribers
- **Decoupled**: Publishers don't know about subscribers
- **Scalable**: Add subscribers without changing publisher

### 2. Topics

Topics are hierarchical strings like file paths:
```
digital_twin/lab/sensor/temperature
│           │   │      └─ Measurement type
│           │   └──────── Data source
│           └──────────── Application
└──────────────────────── Domain
```

Subscribers can use wildcards:
- `+` = single level: `digital_twin/+/sensor/temperature`
- `#` = multiple levels: `digital_twin/lab/#`

### 3. Quality of Service (QoS)

- **QoS 0**: At most once (fire and forget)
  - Fast, no guarantees
  - Used in this lab for simplicity

- **QoS 1**: At least once (acknowledged)
  - Broker confirms receipt
  - May get duplicates

- **QoS 2**: Exactly once (handshake)
  - Four-way handshake ensures single delivery
  - Slowest but guaranteed

### 4. Broker

The central hub that:
- Accepts connections from clients
- Receives published messages
- Routes messages to subscribers
- Maintains subscriptions
- Handles QoS guarantees

---

## Implementation Details

### Sensor Publisher (`sensor_publisher.py`)

**Temperature Generation**:
```python
# Realistic sensor simulation with:
- Gaussian noise (σ = 0.3°C)     # Measurement precision
- Environmental drift (±0.1°C/s)  # Slow changes
- Bounded variation (±3°C)        # Prevents runaway
```

**JSON Payload Structure**:
```json
{
  "timestamp_utc": "2024-01-15T14:23:45.123456Z",  // ISO 8601
  "sensor_id": "TEMP_SENSOR_001",
  "value": 22.4,
  "unit": "Celsius",
  "metadata": {
    "location": "Lab Environment",
    "sensor_type": "Simulated Thermistor",
    "firmware_version": "1.0.0"
  }
}
```

**Key Features**:
- UTC timestamps for global synchronization
- Unique sensor ID for multi-sensor scenarios
- Metadata for context and traceability
- Clean disconnect on Ctrl+C

### Digital Twin Subscriber (`twin_subscriber.py`)

**State Management**:
```python
class DigitalTwinState:
    - temperature_buffer: deque(maxlen=50)  # Circular buffer
    - Statistics: mean, min, max, stdev
    - Anomaly detection: Z-score > 3.0
    - Message counting and session tracking
```

**Anomaly Detection**:
Uses **Z-score** (standard score):
```
z = (x - μ) / σ

If |z| > 3.0:  # More than 3 std deviations from mean
    → Flag as anomaly
```

**Callback Pattern**:
```python
on_connect()    → Subscribe to topics
on_message()    → Process incoming data
on_subscribe()  → Confirm subscription
on_disconnect() → Handle connection loss
```

---

## Running the Lab

### Prerequisites

1. **Install Mosquitto MQTT Broker**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mosquitto mosquitto-clients

   # macOS
   brew install mosquitto

   # Windows
   # Download from https://mosquitto.org/download/
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Step-by-Step Execution

**Terminal 1 - Start MQTT Broker**:
```bash
mosquitto -v
```

Expected output:
```
1737028800: mosquitto version 2.0.11 starting
1737028800: Using default config.
1737028800: Opening ipv4 listen socket on port 1883.
```

**Terminal 2 - Start Sensor Publisher**:
```bash
python sensor_publisher.py
```

Expected output:
```
======================================================================
MQTT SENSOR PUBLISHER - Temperature Sensor Simulation
======================================================================
✓ Connected to MQTT broker at localhost:1883
  Publishing to topic: digital_twin/lab/sensor/temperature
  Sensor ID: TEMP_SENSOR_001
  Publish interval: 2 seconds

[14:23:45] Message #1
  Topic: digital_twin/lab/sensor/temperature
  Temperature: 22.3°C
  Status: ✓ Published successfully
```

**Terminal 3 - Start Digital Twin Subscriber**:
```bash
python twin_subscriber.py
```

Expected output:
```
======================================================================
MQTT DIGITAL TWIN SUBSCRIBER
======================================================================
✓ Connected to MQTT broker at localhost:1883
  Twin ID: COFFEE_SHOP_TWIN_001
  Subscribing to topic: digital_twin/lab/sensor/temperature

[14:23:47] Message #1
  Topic: digital_twin/lab/sensor/temperature
  Sensor: TEMP_SENSOR_001
  Temperature: 22.3°C

📊 Statistics (last 10 readings):
   Mean: 22.1°C  |  Range: [21.8, 22.4]°C  |  σ: 0.19°C
```

### Testing Scenarios

1. **Basic Operation**:
   - Start all three components
   - Observe message flow for 30-60 seconds
   - Verify timestamps and statistics

2. **Connection Resilience**:
   - Stop publisher (Ctrl+C)
   - Subscriber waits gracefully
   - Restart publisher → subscriber resumes

3. **Late Joining**:
   - Start publisher first
   - Start subscriber 30 seconds later
   - Subscriber catches up (no historical backlog with QoS 0)

4. **Broker Restart**:
   - Stop broker (Ctrl+C)
   - Clients attempt reconnection
   - Restart broker → clients reconnect automatically

5. **Multiple Subscribers**:
   - Run twin_subscriber.py in multiple terminals
   - Each receives same messages (Pub/Sub fan-out)

---

## Understanding the Output

### Publisher Console

```
[14:23:45] Message #1
  Topic: digital_twin/lab/sensor/temperature
  Temperature: 22.3°C
  Payload: {"timestamp_utc": "2024-01-15T14:23:45.123456Z", ...}
  Status: ✓ Published successfully
```

- **Timestamp**: Local time of publish
- **Message number**: Incremental counter
- **Temperature**: Current reading with noise/drift
- **Full payload**: JSON structure sent to broker
- **Status**: Confirms successful publish (QoS 0 local only)

### Subscriber Console

```
[14:23:47] Message #10
  Topic: digital_twin/lab/sensor/temperature
  Sensor: TEMP_SENSOR_001
  Temperature: 22.4°C
  Timestamp: 2024-01-15T14:23:45.123456Z

  📊 Statistics (last 10 readings):
     Mean: 22.1°C  |  Range: [21.8, 22.4]°C  |  σ: 0.19°C
```

- **Message count**: Total received (may differ from publisher if started late)
- **Topic**: Confirms which topic delivered this message
- **Sensor metadata**: Identifies data source
- **Statistics**: Updated every 10 messages
  - **Mean**: Average of buffered readings
  - **Range**: [Min, Max] observed
  - **σ (sigma)**: Standard deviation (data spread)

### Anomaly Detection

If a temperature suddenly spikes:
```
  Temperature: 28.5°C
  ⚠ ANOMALY DETECTED! (Total: 1)
```

This triggers when: `|z-score| > 3.0`

Reasons for anomalies in this simulation:
- Random noise spike (unlikely but possible)
- Environmental drift accumulation (constrained by bounds)
- In real systems: sensor malfunction, actual environmental event

---

## Extension Ideas

### 1. Bidirectional Control

Implement a **control publisher** that sends commands back:

```python
# twin_controller.py
control_payload = {
    "command": "SET_THRESHOLD",
    "value": 25.0,
    "timestamp": datetime.utcnow().isoformat()
}
client.publish("digital_twin/lab/control/commands", json.dumps(control_payload))
```

Update sensor_publisher.py to subscribe to control topic and adjust behavior.

### 2. Multiple Sensors

Modify publisher to simulate multiple sensors:
```python
sensors = ["TEMP_001", "TEMP_002", "TEMP_003"]
for sensor_id in sensors:
    topic = f"digital_twin/lab/sensor/{sensor_id}/temperature"
    client.publish(topic, payload)
```

Update subscriber to use wildcard:
```python
TOPIC = "digital_twin/lab/sensor/+/temperature"
```

### 3. Data Persistence

Add database storage to subscriber:
```python
import sqlite3

def on_message(client, userdata, msg):
    sensor_data = json.loads(msg.payload)
    conn = sqlite3.connect('twin_data.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO readings (timestamp, sensor_id, value)
        VALUES (?, ?, ?)
    """, (sensor_data['timestamp_utc'],
          sensor_data['sensor_id'],
          sensor_data['value']))
    conn.commit()
    conn.close()
```

### 4. Real-Time Visualization

Use matplotlib animation:
```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
x_data, y_data = [], []

def animate(frame):
    ax.clear()
    ax.plot(x_data, y_data)
    ax.set_xlabel('Time')
    ax.set_ylabel('Temperature (°C)')

def on_message(client, userdata, msg):
    sensor_data = json.loads(msg.payload)
    x_data.append(datetime.now())
    y_data.append(sensor_data['value'])

ani = FuncAnimation(fig, animate, interval=1000)
plt.show()
```

### 5. QoS Experimentation

Change QoS levels and observe behavior:
```python
# Publisher
client.publish(TOPIC, payload, qos=1)  # At least once

# Subscriber
client.subscribe(TOPIC, qos=1)  # At least once
```

Then test:
- Disconnect broker briefly → QoS 1 buffers messages
- With QoS 0 → messages lost during disconnect

### 6. Last Will and Testament (LWT)

Detect sensor failures:
```python
# In publisher
client.will_set(
    "digital_twin/lab/sensor/status",
    payload=json.dumps({"sensor_id": SENSOR_ID, "status": "offline"}),
    qos=1,
    retain=True
)
```

Broker publishes this "will" if publisher disconnects ungracefully.

---

## Troubleshooting

### "Connection refused" Error

**Problem**: Cannot connect to broker at localhost:1883

**Solutions**:
1. Verify Mosquitto is running: `ps aux | grep mosquitto`
2. Check if port is in use: `netstat -an | grep 1883`
3. Try starting broker with verbose flag: `mosquitto -v`
4. Check firewall settings (Windows/Linux)

### "Invalid JSON" Error

**Problem**: Subscriber reports malformed JSON

**Solutions**:
1. Check publisher is using `json.dumps()` for serialization
2. Verify encoding is UTF-8: `payload.encode('utf-8')`
3. Inspect raw payload in Mosquitto console:
   ```bash
   mosquitto_sub -h localhost -t "digital_twin/lab/sensor/#" -v
   ```

### Messages Not Received

**Problem**: Publisher sends, but subscriber doesn't receive

**Solutions**:
1. Verify both use same topic string (case-sensitive!)
2. Check subscriber is connected before publisher starts sending
3. Try QoS 1 to eliminate message loss
4. Verify broker is routing:
   ```bash
   # In broker console, look for:
   # Received PUBLISH from SensorPublisher
   # Sending PUBLISH to TwinSubscriber
   ```

### High Anomaly Count

**Problem**: Many anomalies detected even with normal data

**Solutions**:
1. Increase threshold: `ANOMALY_THRESHOLD = 4.0` (more tolerant)
2. Increase buffer size: `BUFFER_SIZE = 100` (better statistics)
3. Wait for buffer to fill before anomaly detection (currently needs 10 samples)

---

## Key Takeaways

1. **MQTT Enables Loose Coupling**
   - Sensors don't need to know about Digital Twins
   - Digital Twins don't control sensor timing
   - Broker handles all routing and buffering

2. **Pub/Sub Scales Naturally**
   - Add more sensors → more publishers
   - Add more twins → more subscribers
   - No N×M connections, just N+M to broker

3. **JSON Provides Flexibility**
   - Self-describing data structure
   - Easy to extend with new fields
   - Language-agnostic (Python, JavaScript, C++, etc.)

4. **Callbacks Enable Asynchrony**
   - Don't poll for data, react to events
   - Non-blocking architecture
   - Efficient resource usage

5. **Digital Twins Need More Than Data**
   - Statistical analysis for trends
   - Anomaly detection for health monitoring
   - Historical buffering for prediction
   - Metadata for context awareness

---

## Next Steps

With MQTT mastered, you can:

1. **Integrate with Previous Labs**:
   - Publish Coffee Shop simulation state (Lab 2) via MQTT
   - Subscribe to AGV positions (Lab 3) for digital twin
   - Stream DC Motor telemetry (Lab 5) to cloud

2. **Explore Cloud Platforms**:
   - AWS IoT Core (MQTT broker as a service)
   - Azure IoT Hub
   - Google Cloud IoT Core
   - HiveMQ Cloud

3. **Add Security**:
   - TLS/SSL encryption (port 8883)
   - Username/password authentication
   - Client certificate authentication
   - ACLs for topic-based access control

4. **Implement Edge Computing**:
   - Run broker on Raspberry Pi
   - Local processing before cloud upload
   - Hierarchical broker architecture (edge → cloud)

---

## References

### MQTT Specification
- [MQTT v5.0 Specification](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
- [MQTT Essentials](https://www.hivemq.com/mqtt-essentials/) - Excellent tutorial series

### Mosquitto Documentation
- [Official Mosquitto Site](https://mosquitto.org/)
- [Mosquitto Man Pages](https://mosquitto.org/man/)

### Paho MQTT Python Client
- [GitHub Repository](https://github.com/eclipse/paho.mqtt.python)
- [API Documentation](https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html)

### Digital Twin Communication Patterns
- Grieves, M., & Vickers, J. (2017). "Digital Twin: Mitigating Unpredictable, Undesirable Emergent Behavior"
- Tao, F., et al. (2019). "Digital Twin Driven Prognostics and Health Management for Complex Equipment"

---

## Summary

This lab introduced **MQTT as the communication backbone for Digital Twins**. You built a complete data pipeline:
- **Sensor**: Generates realistic telemetry
- **Broker**: Routes messages reliably
- **Twin**: Maintains synchronized state with analytics

You experienced firsthand why MQTT dominates IoT:
- **Lightweight protocol** for constrained devices
- **Publish/Subscribe pattern** for scalability
- **Asynchronous messaging** for decoupled systems
- **Topic-based routing** for flexible architectures

These concepts form the foundation of **real-world Digital Twin implementations** across manufacturing, automotive, smart cities, and healthcare.

**Congratulations on completing Lab 6!** You now have the skills to connect physical and digital worlds.
