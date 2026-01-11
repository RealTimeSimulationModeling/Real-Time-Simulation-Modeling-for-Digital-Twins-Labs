# Lab 6: MQTT Data Link - Quick Start Guide

## What This Lab Does

Demonstrates **MQTT Publish/Subscribe** communication between a simulated sensor and a Digital Twin application.

**Architecture**: Sensor Publisher → MQTT Broker → Digital Twin Subscriber

---

## 30-Second Setup

### 1. Install MQTT Broker (Mosquitto)

**Ubuntu/Debian**:
```bash
sudo apt-get install mosquitto mosquitto-clients
```

**macOS**:
```bash
brew install mosquitto
```

**Windows**:
Download from [https://mosquitto.org/download/](https://mosquitto.org/download/)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

That's it! You're ready to run.

---

## Running the Lab

You'll need **three terminal windows**:

### Terminal 1: Start MQTT Broker
```bash
mosquitto -v
```

Expected output:
```
1737028800: mosquitto version 2.0.11 starting
1737028800: Using default config.
1737028800: Opening ipv4 listen socket on port 1883.
```

### Terminal 2: Start Sensor Publisher
```bash
python sensor_publisher.py
```

Expected output:
```
✓ Connected to MQTT broker at localhost:1883
  Publishing to topic: digital_twin/lab/sensor/temperature

[14:23:45] Message #1
  Temperature: 22.3°C
  Status: ✓ Published successfully
```

### Terminal 3: Start Digital Twin Subscriber
```bash
python twin_subscriber.py
```

Expected output:
```
✓ Connected to MQTT broker at localhost:1883
✓ Subscription confirmed

[14:23:47] Message #1
  Sensor: TEMP_SENSOR_001
  Temperature: 22.3°C

📊 Statistics (last 10 readings):
   Mean: 22.1°C  |  Range: [21.8, 22.4]°C  |  σ: 0.19°C
```

---

## What You Should Observe

1. **Broker Console**: Shows connections and message flow
   ```
   New client connected from 127.0.0.1 as SensorPublisher
   New client connected from 127.0.0.1 as TwinSubscriber
   Received PUBLISH from SensorPublisher (...)
   Sending PUBLISH to TwinSubscriber (...)
   ```

2. **Publisher Console**: Sends temperature readings every 2 seconds
   - Message counter increments
   - Temperature varies with noise (±0.3°C) and drift
   - JSON payload shown with timestamp and metadata

3. **Subscriber Console**: Receives messages asynchronously
   - Displays each reading with timestamp
   - Shows statistics every 10 messages
   - Detects anomalies (rare with normal operation)

---

## Key Controls

- **Stop any component**: Press `Ctrl+C`
- **View final stats**: Subscriber shows summary on shutdown
- **Monitor broker**: Check Terminal 1 for connection/message events

---

## Testing Scenarios

### Scenario 1: Connection Resilience
1. Start all three components
2. Stop publisher (Ctrl+C in Terminal 2)
3. **Observe**: Subscriber waits gracefully, no errors
4. Restart publisher: `python sensor_publisher.py`
5. **Observe**: Communication resumes immediately

### Scenario 2: Late Joining Subscriber
1. Start broker and publisher only (Terminals 1 & 2)
2. Wait 30 seconds
3. Start subscriber (Terminal 3)
4. **Observe**: Subscriber starts receiving from "now" (no backlog with QoS 0)

### Scenario 3: Multiple Subscribers (Pub/Sub Fan-out)
1. Keep broker and publisher running
2. Open two more terminals
3. Run `python twin_subscriber.py` in each
4. **Observe**: All subscribers receive same messages independently

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Verify Mosquitto is running: `ps aux \| grep mosquitto` |
| No messages in subscriber | Check topic names match exactly (case-sensitive!) |
| "Invalid JSON" error | Restart publisher and subscriber in correct order |
| Broker not starting | Check if port 1883 is already in use: `netstat -an \| grep 1883` |

---

## Understanding the Output

### Statistics Explained

```
📊 Statistics (last 50 readings):
   Mean: 22.1°C  |  Range: [21.8, 22.4]°C  |  σ: 0.19°C
```

- **Mean**: Average temperature over buffered readings
- **Range**: [Minimum, Maximum] observed
- **σ (sigma)**: Standard deviation (how spread out the data is)
  - Small σ (< 0.5): Very stable measurements
  - Large σ (> 1.0): High variability

### Anomaly Detection

```
⚠ ANOMALY DETECTED! (Total: 1)
```

Triggers when reading is **> 3 standard deviations** from mean.

In this simulation, anomalies are rare (noisy sensor is within ±3σ bounds).

In real systems, indicates:
- Sensor malfunction
- Actual environmental event (fire, equipment failure)
- Need for maintenance or investigation

---

## What's Happening Under the Hood

### Publisher (sensor_publisher.py)
```python
# Generate temperature with noise
temperature = generate_temperature_reading()  # 22.3°C

# Package into JSON
payload = {
    "timestamp_utc": "2024-01-15T14:23:45.123456Z",
    "sensor_id": "TEMP_SENSOR_001",
    "value": 22.3,
    "unit": "Celsius"
}

# Publish to broker
client.publish("digital_twin/lab/sensor/temperature", json.dumps(payload))
```

### Broker (Mosquitto)
```
1. Receives message from publisher
2. Checks for subscribers to matching topics
3. Delivers copy to each subscriber
4. Handles QoS, buffering, retries
```

### Subscriber (twin_subscriber.py)
```python
# Callback fires when message arrives
def on_message(client, userdata, msg):
    sensor_data = json.loads(msg.payload)  # Parse JSON
    twin_state.update(sensor_data)         # Update internal state

    # Calculate statistics
    stats = twin_state.get_statistics()
    print(f"Mean: {stats['mean']}°C")

    # Detect anomalies
    if is_anomaly(sensor_data['value']):
        print("⚠ ANOMALY DETECTED!")
```

---

## Key MQTT Concepts Demonstrated

1. **Publish/Subscribe Pattern**
   - Publisher doesn't know about subscribers
   - Subscribers don't control publisher
   - Broker decouples components

2. **Topics as Routing Keys**
   - Hierarchical: `digital_twin/lab/sensor/temperature`
   - Enables flexible subscriptions with wildcards
   - Multiple subscribers can receive same data

3. **Asynchronous Communication**
   - Publisher sends when ready
   - Subscriber receives via callback
   - No polling, no blocking

4. **Quality of Service (QoS)**
   - QoS 0: "Fire and forget" (used here)
   - Fast, minimal overhead
   - May lose messages if network drops

---

## Next Steps

1. **Read the Full README.md** for:
   - Detailed architecture diagrams
   - Line-by-line code explanations
   - Extension ideas (control, persistence, visualization)
   - Production deployment considerations

2. **Experiment with Parameters**:
   - Change `PUBLISH_INTERVAL` in sensor_publisher.py
   - Adjust `ANOMALY_THRESHOLD` in twin_subscriber.py
   - Modify `BUFFER_SIZE` to change statistics window

3. **Try Extensions**:
   - Add more sensor types (humidity, pressure)
   - Implement bidirectional control
   - Store data in SQLite database
   - Create real-time matplotlib visualization

4. **Integrate with Other Labs**:
   - Publish Coffee Shop simulation state (Lab 2) via MQTT
   - Stream DC Motor telemetry (Lab 5) to Digital Twin

---

## Summary

You've built a complete **MQTT-based data link** between a sensor and Digital Twin:

- ✅ Installed and ran Mosquitto broker
- ✅ Simulated sensor publishing telemetry
- ✅ Digital Twin subscribing and analyzing data
- ✅ JSON serialization for structured payloads
- ✅ Statistical analysis and anomaly detection

This pattern scales from **single sensors to millions** and is used in production by:
- AWS IoT Core
- Azure IoT Hub
- Industrial automation (SCADA systems)
- Smart home platforms
- Automotive telemetry

**You now have the skills to build IoT data pipelines for Digital Twins!**

---

## Quick Reference

### Start Everything (3 terminals)
```bash
# Terminal 1
mosquitto -v

# Terminal 2
python sensor_publisher.py

# Terminal 3
python twin_subscriber.py
```

### Stop Everything
Press `Ctrl+C` in each terminal (order doesn't matter)

### Monitor MQTT Traffic (Optional - 4th terminal)
```bash
# Subscribe to all topics under digital_twin/
mosquitto_sub -h localhost -t "digital_twin/#" -v
```

Shows raw MQTT messages for debugging.

---

For detailed explanations, see **README.md**.
