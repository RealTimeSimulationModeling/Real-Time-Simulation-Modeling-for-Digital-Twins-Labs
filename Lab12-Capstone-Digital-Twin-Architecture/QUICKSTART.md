# Quick Start Guide - Capstone Project

**Get started on your Digital Twin Architecture Design in 30 minutes**

---

## What You Need to Know Right Now

1. **This is a DESIGN project** - you create diagrams and documentation, NOT code
2. **Deliverables**: Architectural diagram + 8-10 page design document
3. **System**: Use the Hybrid Factory Model from Lab 8 (recommended)
4. **Framework**: Address all 5 dimensions of the Digital Twin model
5. **Time needed**: 25-35 hours total; start 3-4 weeks before deadline

---

## First 30 Minutes: Get Oriented

### Minute 0-10: Read This First

**Three essential documents** (in this order):

1. **README.md** ← Start here for overview
2. **PROJECT_SPECIFICATION.md** ← Complete requirements (read thoroughly!)
3. **RUBRIC.md** ← How you'll be graded (100 points)

**Also available**:
- **DESIGN_TEMPLATE.md** ← Template for your document (use this as starting point)

### Minute 10-20: Understand the Framework

Your design MUST address **5 dimensions**:

#### 1. Physical Entity (PE)
*The real-world system*
- What sensors? (temperature, vibration, current...)
- What actuators? (motor controllers, valves...)
- What edge devices? (industrial PCs, PLCs...)
- What protocols? (Modbus, OPC-UA...)

#### 2. Virtual Entity (VE)
*The digital model*
- Which simulation paradigm? (DES, ABM, SD, hybrid?)
- How is it parameterized?
- How is state synchronized? (Kalman filter from Lab 7?)
- How do you quantify uncertainty? (Monte Carlo from Lab 9?)

#### 3. Data (D)
*Information storage*
- What databases? (TimescaleDB for time-series? PostgreSQL? MongoDB? Redis?)
- What schemas? (JSON examples)
- How much data? (Calculate volumes: sensors × frequency × days)
- What retention policies?

#### 4. Connection (C)
*Communication*
- MQTT broker architecture (single? clustered?)
- Topic hierarchy (e.g., `factory/line1/machine/temperature`)
- QoS levels (0, 1, or 2 for each topic type?)
- APIs (REST endpoints? WebSockets?)
- Latency budgets (sensor → edge: <100ms?)

#### 5. Services (S)
*Applications and deployment*
- Which microservices? (data ingestion, simulation, API, dashboard...)
- Docker containers (what's in each?)
- Kubernetes deployment (how many pods? scaling rules?)
- Monitoring (Prometheus, Grafana?)
- Security (TLS, authentication, RBAC?)

### Minute 20-30: Quick Decision Checklist

Make these high-level decisions now (you'll detail them later):

**System Selection**:
- [ ] Using Hybrid Factory Model from Lab 8? **→ Recommended**
- [ ] Or alternative system? **→ Needs instructor approval**

**Deployment Strategy**:
- [ ] Edge-heavy (most processing local)
- [ ] Cloud-heavy (most processing in cloud)
- [ ] **Hybrid (edge for control, cloud for analytics)** ← Recommended

**Service Architecture**:
- [ ] Monolithic (single application)
- [ ] **Microservices (separate services)** ← Recommended for complexity

**Key Technologies** (initial choices, can refine):
- [ ] **MQTT** for IoT messaging (Mosquitto? EMQX?)
- [ ] **TimescaleDB** for time-series data
- [ ] **PostgreSQL** for relational data
- [ ] **Redis** for caching/real-time
- [ ] **Docker** for containerization
- [ ] **Kubernetes** for orchestration
- [ ] **Prometheus + Grafana** for monitoring

---

## Next 2 Hours: Initial Architecture Sketch

### Hour 1: Sketch Physical and Virtual Layers

**On paper or whiteboard**, draw:

1. **Physical Layer** (bottom):
   ```
   [Sensor: Temp] [Sensor: Vibration] [Sensor: Current]
         ↓                ↓                  ↓
   [Edge Device: Raspberry Pi + Mosquitto MQTT]
         ↓
   [Network: VPN tunnel to cloud]
   ```

2. **Virtual Layer** (cloud):
   ```
   [Simulation Service: Hybrid Factory Model]
       - DES (production flow)
       - ABM (technician agents)
       - SD (machine health degradation)

   [State Estimator: Kalman Filter]

   [Optimization Service: Nightly schedule optimization]
   ```

3. **Data Layer** (alongside virtual):
   ```
   [TimescaleDB: sensor telemetry]
   [PostgreSQL: asset registry, users]
   [MongoDB: scenario results]
   [Redis: dashboard cache]
   ```

### Hour 2: Sketch Services and Communication

4. **Services Layer**:
   ```
   [Data Ingestion] ← MQTT subscriber
   [Simulation Engine] ← Base twin + scenario workers
   [API Gateway] ← Kong
   [Dashboard] ← React.js + WebSocket
   [Optimization] ← Scheduled jobs
   ```

5. **Communication Flows**:
   ```
   Sensors → MQTT (edge) → MQTT (cloud) → Data Ingestion → TimescaleDB
                                                        ↓
   Simulation Engine ← State Estimator ← TimescaleDB
         ↓
   MQTT predictions → Dashboard (WebSocket) → Operator
   ```

**Deliverable**: Rough sketch showing all major components and data flows

---

## Week 1 Goals (8-10 hours)

### Day 1-2: Research Technologies (3 hours)

**MQTT**:
- [ ] Read MQTT basics: https://mqtt.org/
- [ ] Understand QoS levels (0, 1, 2)
- [ ] Review Lab 6 (MQTT Data Link)

**Databases**:
- [ ] TimescaleDB docs: https://docs.timescale.com/
- [ ] When to use time-series vs relational vs document?
- [ ] Calculate your data volumes (50 sensors × 1 Hz × 500 bytes = ?)

**Docker & Kubernetes**:
- [ ] Docker basics: https://docs.docker.com/get-started/
- [ ] Kubernetes concepts: https://kubernetes.io/docs/concepts/
- [ ] Key resources: Deployments, Services, ConfigMaps, Secrets, HPA

### Day 3-4: Write Physical Entity Section (3 hours)

Using **DESIGN_TEMPLATE.md** section 2:

- [ ] List all sensors (type, location, sampling rate, accuracy)
- [ ] List all actuators (type, control range, response time)
- [ ] Specify edge devices (hardware, responsibilities)
- [ ] Identify communication protocols (OPC-UA, Modbus, etc.)
- [ ] Address time synchronization (NTP? PTP?)
- [ ] Note safety requirements

**Target**: 1 page, comprehensive sensor/actuator inventory

### Day 5-7: Write Virtual Entity Section (4 hours)

Using **DESIGN_TEMPLATE.md** section 3:

- [ ] Justify simulation paradigm (why hybrid DES+ABM+SD?)
- [ ] Describe model architecture (reference Lab 8)
- [ ] Explain state estimation approach (Kalman filter from Lab 7)
- [ ] Discuss uncertainty quantification (Monte Carlo from Lab 9)
- [ ] List predictive scenarios (maintenance, production planning, resource allocation)

**Target**: 1.5 pages, clear virtual model architecture

---

## Week 2 Goals (8-10 hours)

### Day 1-2: Write Data Section (3 hours)

Using **DESIGN_TEMPLATE.md** section 4:

- [ ] Define data taxonomy (telemetry, events, commands, KPIs)
- [ ] Provide example schemas (JSON for sensor message, event, etc.)
- [ ] Select databases with justification table
- [ ] Calculate data volumes (sensors × frequency × size × retention)
- [ ] Specify retention policies (raw: 90 days, aggregated: 1 year)
- [ ] Address security (encryption at rest/in transit)

**Target**: 1 page with quantitative volume estimates

### Day 3-5: Write Connection Section (5 hours)

Using **DESIGN_TEMPLATE.md** section 5:

- [ ] Design MQTT topic hierarchy (complete tree structure)
  ```
  factory/
    production/
      line1/
        machine/
          telemetry/temperature (QoS 0)
          status/health (QoS 1)
          command/maintenance (QoS 2)
  ```
- [ ] Specify QoS levels per topic type (table)
- [ ] Define REST API endpoints (GET/POST with paths)
- [ ] Provide example request/response
- [ ] Calculate latency budget (sensor → edge: <100ms, edge → cloud: <1s)
- [ ] Calculate bandwidth (sensors × frequency × size = Kbps)
- [ ] Describe failure modes (cloud disconnect, broker crash, sensor failure)

**Target**: 1.5 pages with complete MQTT hierarchy

---

## Week 3 Goals (8-10 hours)

### Day 1-3: Write Services Section (6 hours)

Using **DESIGN_TEMPLATE.md** section 6:

For EACH service:
1. **Data Ingestion Service**
   - Responsibility, technology, inputs, outputs, scaling, resources

2. **Simulation Service**
   - Base twin (1 replica) + scenario workers (HPA 2-10)

3. **State Estimation Service**
   - Kalman filter, per-asset instances

4. **Optimization Service**
   - Batch jobs (Kubernetes CronJob)

5. **API Gateway**
   - Kong, authentication, routing

6. **Dashboard Service**
   - React.js, WebSocket

7. **Database Services**
   - TimescaleDB, PostgreSQL, MongoDB, Redis

- [ ] Create service decomposition diagram
- [ ] Write Kubernetes Deployment YAML example (for simulation service)
- [ ] Write Kubernetes HPA example (for scenario workers)
- [ ] Specify monitoring (Prometheus metrics, Grafana dashboards)
- [ ] Specify security (authentication, TLS, RBAC, secrets)

**Target**: 2 pages, complete service architecture

### Day 4-5: Write Deployment & Operations + Alternatives (2 hours)

Using **DESIGN_TEMPLATE.md** sections 7-8:

**Deployment**:
- [ ] CI/CD pipeline (GitHub Actions → Docker build → ArgoCD deploy)
- [ ] Environments (dev, staging, production)
- [ ] Rollout strategy (rolling update, blue-green for critical services)
- [ ] Backup (daily TimescaleDB to S3, 30-day retention)

**Alternatives**:
- [ ] Monolithic vs microservices (pros, cons, why rejected)
- [ ] Cloud-only vs hybrid (pros, cons, why rejected)
- [ ] Alternative database (InfluxDB vs TimescaleDB, why rejected)

**Target**: 1 page total

### Day 6: Write System Overview + Conclusion (2 hours)

Using **DESIGN_TEMPLATE.md** sections 1 and 10:

**System Overview**:
- [ ] System description (what does the factory do?)
- [ ] Business objectives (reduce downtime, optimize throughput)
- [ ] KPIs (MTBF, OEE, throughput - with targets)
- [ ] Scope and boundaries (what's included/excluded)

**Conclusion**:
- [ ] Summary of key decisions
- [ ] Expected benefits (quantify if possible: "30% downtime reduction")
- [ ] Known limitations and mitigations

**Target**: 1.5 pages total

---

## Week 4 Goals (6-8 hours)

### Day 1-3: Create Professional Diagram (4 hours)

**Tool**: draw.io (https://app.diagrams.net/)

**Layers to show**:
1. Physical (sensors, actuators, edge devices)
2. Communication (MQTT brokers, network)
3. Data (databases with icons)
4. Simulation (virtual models)
5. Services (microservices as boxes)
6. Deployment (Docker containers, K8s pods)
7. User (dashboards, APIs)

**Requirements**:
- [ ] All components labeled with technology (e.g., "MQTT: Mosquitto")
- [ ] Data flows as arrows with protocols (MQTT QoS 1, HTTP/REST, gRPC)
- [ ] Logical grouping (edge box, cloud box)
- [ ] Legend (symbols explained)
- [ ] High resolution (export as PDF or PNG ≥1920px wide)

**Pro tip**: Use layers in draw.io to organize (physical layer, communication layer, etc.)

### Day 4-5: Review and Polish (3 hours)

**Content Review**:
- [ ] Read entire document start to finish
- [ ] Check against rubric (self-score each category)
- [ ] Verify all 5 dimensions addressed
- [ ] Ensure all decisions justified
- [ ] Confirm quantitative analysis present

**Quality Review**:
- [ ] Proofread for typos (use Grammarly or similar)
- [ ] Check formatting consistency
- [ ] Verify page numbers and headers
- [ ] Ensure diagram is readable
- [ ] Check citations in references section

**Self-Assessment**:
- [ ] Architectural Completeness: ___ / 25
- [ ] Technical Depth: ___ / 25
- [ ] Design Quality: ___ / 20
- [ ] Documentation Quality: ___ / 15
- [ ] Decision Justification: ___ / 10
- [ ] Innovation: ___ / 5
- [ ] **Total**: ___ / 100 (target: 85+)

If < 85: identify weakest sections and strengthen before submission

### Day 6: Package and Submit (1 hour)

**Create submission package**:
```
LastName_FirstName_DigitalTwinArchitecture.zip
├── README.md
├── architecture_diagram.pdf
├── design_document.pdf
└── references.md
```

**Final checks**:
- [ ] All files included
- [ ] ZIP file named correctly
- [ ] Document is PDF (not Word)
- [ ] Diagram is high resolution
- [ ] Submitted before deadline

---

## Emergency: Only 1 Week Left?

**Minimum viable project** (50-60 hours condensed to 20):

### Day 1-2 (6 hours): Research + Rough Sketch
- Skim PROJECT_SPECIFICATION.md (1 hour)
- Research MQTT, databases, Kubernetes (2 hours)
- Sketch architecture on paper (3 hours)

### Day 3-4 (8 hours): Write Core Sections
Focus on highest-value sections:
- System Overview (1 hour)
- Physical Entity (1.5 hours)
- Virtual Entity (1.5 hours)
- Data (1.5 hours)
- Connection (2.5 hours)

### Day 5-6 (8 hours): Write Services + Create Diagram
- Services section (4 hours) - focus on 3-4 key microservices
- Professional diagram (4 hours)

### Day 7 (4 hours): Write Remaining + Polish
- Deployment (1 hour)
- Alternatives (30 min)
- Conclusion (30 min)
- Executive Summary (30 min - write last!)
- Review + proofread (1.5 hours)

**Warning**: This compressed schedule will likely yield a B grade (75-85 points). To get A (85+), you need time for depth and polish.

---

## Top 5 Tips for Success

### 1. Be Specific
❌ "We use a database."
✅ "TimescaleDB 2.11 for time-series data, chosen for 10:1 compression and SQL compatibility."

### 2. Justify Everything
❌ "The system uses microservices."
✅ "Microservices allow independent scaling (simulation needs 4 CPU, API needs 0.5 CPU). Trade-off: increased complexity."

### 3. Calculate Numbers
❌ "The system stores sensor data."
✅ "50 sensors × 1 Hz × 500 bytes × 365 days = 788 GB/year. With 10:1 compression: 79 GB."

### 4. Consider Alternatives
❌ [No alternatives discussed]
✅ "Considered monolithic (simpler) but rejected due to inflexible scaling."

### 5. Professional Presentation
❌ Hand-drawn sketch with arrows everywhere
✅ Clean draw.io diagram with aligned boxes, labeled flows, legend

---

## Quick Reference: Required Technologies to Specify

Check off as you include in your design:

**IoT/Communication**:
- [ ] MQTT broker (Mosquitto, EMQX, or similar)
- [ ] Topic hierarchy designed
- [ ] QoS levels specified
- [ ] Industrial protocols if applicable (OPC-UA, Modbus)

**Databases**:
- [ ] Time-series database (TimescaleDB, InfluxDB, Prometheus)
- [ ] Relational database (PostgreSQL, MySQL)
- [ ] Cache (Redis, Memcached)
- [ ] Optional: Document store (MongoDB), Message queue (RabbitMQ, Kafka)

**Simulation**:
- [ ] SimPy for DES (from Lab 8)
- [ ] Custom ABM agents (from Lab 8)
- [ ] NumPy/SciPy for SD (from Lab 8)

**Deployment**:
- [ ] Docker (containerization)
- [ ] Kubernetes (orchestration)
- [ ] Kubernetes resources: Deployment, Service, ConfigMap, Secret, HPA

**Monitoring**:
- [ ] Metrics: Prometheus
- [ ] Visualization: Grafana
- [ ] Optional: Logging (Elasticsearch + Kibana), Tracing (Jaeger)

**Security**:
- [ ] TLS/SSL for all communication
- [ ] Authentication (OAuth2, JWT)
- [ ] Authorization (RBAC)
- [ ] Secrets management (Kubernetes Secrets, Vault)

---

## Questions?

**Before asking**:
1. Check the FAQ in PROJECT_SPECIFICATION.md
2. Review the rubric to see if it's addressed there
3. Look at the DESIGN_TEMPLATE.md examples

**Still stuck?**
- Email instructor
- Attend office hours
- Review Labs 1-11 (especially Lab 8 for the Hybrid Factory)

---

## You've Got This!

**Remember**:
- You've already implemented most of these concepts in Labs 1-11
- This project is about **integration and systems thinking**
- Focus on the **5 dimensions** framework
- **Justify** your decisions with trade-offs
- **Be specific** with technology choices
- **Calculate** numbers for data volumes, bandwidth, latency

**Start now. Work steadily. Submit with confidence.**

Good luck! 🎓

---

*Quick Start Guide | Lab 12: Capstone Digital Twin Architecture | IDS 6742*
