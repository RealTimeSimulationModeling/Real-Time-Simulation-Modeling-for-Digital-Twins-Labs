# Final Capstone Project: Production Digital Twin Architecture Design

**IDS 6742: Real-Time Simulation Modeling for Digital Twins**

---

## Project Overview

This capstone project represents the culmination of your learning journey through simulation paradigms, state estimation, predictive analytics, and optimization. You will design a **complete, production-ready Digital Twin architecture** that could be deployed in a real industrial environment.

**Important**: This is a **design project**, not an implementation project. You will create detailed architectural diagrams and comprehensive design documentation, but you will NOT write the full implementation code.

### Learning Objectives

By completing this project, you will demonstrate your ability to:

1. **Architect a complete Digital Twin system** addressing all five dimensions of the Digital Twin model
2. **Make informed technology choices** balancing trade-offs between performance, scalability, cost, and complexity
3. **Design communication patterns** for real-time data exchange between physical and virtual entities
4. **Plan deployment strategies** using modern containerization and orchestration technologies
5. **Apply security best practices** for industrial IoT and cloud systems
6. **Create professional technical documentation** suitable for engineering teams

---

## Deliverables

You will submit **two primary deliverables**:

### 1. Architectural Diagram

A comprehensive, multi-layer architectural diagram showing:

- **Physical layer**: Sensors, actuators, edge devices, PLCs
- **Communication layer**: MQTT brokers, API gateways, network topology
- **Data layer**: Databases, data lakes, message queues, caching
- **Simulation layer**: Digital twin models, state estimators, predictive engines
- **Service layer**: Microservices, APIs, optimization engines
- **Deployment layer**: Docker containers, Kubernetes pods, cloud infrastructure
- **User interface layer**: Dashboards, control panels, operator interfaces

**Format**: High-quality diagram created using tools such as:
- draw.io (diagrams.net)
- Lucidchart
- Microsoft Visio
- PlantUML
- Mermaid diagrams

**Requirements**:
- Clear visual hierarchy and layering
- Technology choices labeled (e.g., "MQTT Broker: Mosquitto", "Database: TimescaleDB")
- Data flow arrows showing direction and protocols
- Legend explaining symbols and colors
- Readable at standard presentation size

### 2. Design Document

A detailed technical design document (8-10 pages) covering all architectural decisions using the **5-Dimension Digital Twin Model** framework.

**Format**: Professional technical document (PDF or Markdown)

**Required Sections**: (See detailed structure below)

---

## System Selection

### Recommended: Hybrid Factory Model

We **strongly recommend** using the **Hybrid Factory Model** from Lab 8 as the subject for your Digital Twin architecture. This model provides:

- **Multiple simulation paradigms** (DES, ABM, SD) requiring sophisticated orchestration
- **Realistic operational complexity** with machines, technicians, maintenance, production
- **Rich data streams** from machine health, production metrics, agent states
- **Clear optimization opportunities** (predictive maintenance, scheduling, resource allocation)
- **Scalability challenges** that justify microservices and cloud deployment

**Alternative Systems** (if you prefer):

You may choose a different system if you have domain expertise or specific interest, such as:

- **Smart Building HVAC System**: Energy optimization with occupancy prediction
- **Logistics Fleet Management**: Vehicle routing with real-time traffic integration
- **Semiconductor Fab**: Wafer processing with equipment degradation
- **Hospital Emergency Department**: Patient flow with resource allocation
- **Wind Farm**: Turbine control with weather prediction

**Requirements for Alternative Systems**:
- Must involve real-time physical processes
- Must require predictive simulation capabilities
- Must generate sufficient data to justify the architecture
- Must have clear business value and KPIs

---

## The 5-Dimension Digital Twin Model Framework

Your design must comprehensively address all five dimensions:

### Dimension 1: Physical Entity (PE)

The real-world system being modeled.

**Design Considerations**:
- What sensors are deployed? (types, sampling rates, accuracy)
- What actuators enable control? (response times, safety limits)
- What edge devices process data locally? (industrial PCs, PLCs, edge gateways)
- What communication protocols connect devices? (OPC-UA, Modbus, industrial Ethernet)
- How is time synchronization maintained? (NTP, PTP/IEEE 1588)
- What are the physical constraints and safety requirements?

### Dimension 2: Virtual Entity (VE)

The digital representation and simulation models.

**Design Considerations**:
- Which simulation paradigm(s) are appropriate? (DES, ABM, SD, physics-based)
- How are models parameterized and validated?
- What is the fidelity trade-off? (detailed vs. fast execution)
- How is model state synchronized with physical state?
- What state estimation techniques are used? (Kalman filters, particle filters)
- How are model uncertainties quantified and communicated?
- What predictive scenarios are supported?

### Dimension 3: Data (D)

The information linking physical and virtual entities.

**Design Considerations**:
- **Data Sources**: What data is collected? (telemetry, events, commands, KPIs)
- **Data Schema**: How is data structured? (JSON, Protocol Buffers, time-series)
- **Data Storage**:
  - Time-series databases (InfluxDB, TimescaleDB, Prometheus)
  - Relational databases (PostgreSQL, MySQL)
  - Document stores (MongoDB)
  - Data lakes (S3, MinIO)
- **Data Volume**: What are the storage and bandwidth requirements?
- **Data Quality**: How is data validated and cleaned?
- **Data Retention**: What is the archival strategy?
- **Data Security**: Encryption, access control, compliance (GDPR, HIPAA)

### Dimension 4: Connection (C)

The bidirectional communication enabling data exchange.

**Design Considerations**:
- **Physical → Virtual** (sensor data ingestion):
  - MQTT topics and QoS levels
  - Message frequency and batching
  - Edge processing and filtering
- **Virtual → Physical** (control commands):
  - Command validation and safety checks
  - Latency requirements
  - Failure modes and fallbacks
- **Network Architecture**:
  - On-premise vs. cloud vs. hybrid
  - Edge computing topology
  - Load balancing and redundancy
- **Protocols**:
  - MQTT (IoT messaging)
  - HTTP/REST (APIs)
  - WebSockets (real-time dashboards)
  - gRPC (service-to-service)

### Dimension 5: Services (S)

The applications and intelligence built on the digital twin.

**Design Considerations**:
- **Monitoring & Visualization**: Real-time dashboards, alerting
- **Predictive Analytics**: Scenario analysis, forecasting
- **Prescriptive Analytics**: Optimization, decision support
- **Automated Control**: Closed-loop control policies
- **Reporting & Analytics**: Historical analysis, KPI tracking
- **Machine Learning**: Anomaly detection, pattern recognition

**Service Architecture**:
- Microservices vs. monolithic
- Service mesh (Istio, Linkerd)
- API gateway (Kong, Traefik)
- Containerization (Docker)
- Orchestration (Kubernetes)

---

## Architectural Decision Points

Your design document must address these critical decisions:

### 1. Deployment Architecture

**Decision**: Where do computational components run?

**Options**:
- **Edge-Heavy**: Maximum local processing, minimal cloud dependency
  - *Pros*: Low latency, works offline, data privacy
  - *Cons*: Limited compute power, harder updates, distributed management
- **Cloud-Heavy**: Centralized processing in cloud
  - *Pros*: Scalability, easy updates, centralized monitoring
  - *Cons*: Latency, requires connectivity, cloud costs
- **Hybrid (Recommended)**: Edge for real-time control, cloud for analytics
  - *Pros*: Best of both worlds, flexible scaling
  - *Cons*: More complex architecture, synchronization challenges

**Your Task**: Choose and justify your deployment strategy for your system.

### 2. Service Architecture

**Decision**: How are software components organized?

**Options**:
- **Monolithic**: Single application with all functionality
  - *Pros*: Simpler deployment, easier testing
  - *Cons*: Tight coupling, hard to scale, single failure point
- **Microservices**: Separate services with clear boundaries
  - *Pros*: Independent scaling, technology flexibility, fault isolation
  - *Cons*: Distributed system complexity, inter-service communication overhead
- **Hybrid**: Core services separated, tightly-coupled features together

**Your Task**: Design service boundaries and justify your decomposition.

### 3. Data Management Strategy

**Decision**: How is data stored, processed, and accessed?

**Components**:
- **Time-Series Database**: For sensor telemetry (InfluxDB, TimescaleDB, Prometheus)
- **Relational Database**: For structured data (PostgreSQL, MySQL)
- **Document Store**: For flexible schemas (MongoDB, Couchbase)
- **Message Queue**: For asynchronous processing (RabbitMQ, Kafka)
- **Cache Layer**: For high-frequency access (Redis, Memcached)
- **Data Lake**: For long-term analytics (S3, MinIO, Hadoop)

**Your Task**: Select appropriate data technologies and design data flow.

### 4. Communication Patterns

**Decision**: How do components exchange information?

**For IoT Layer (Physical ↔ Edge)**:
- **MQTT**: Industry standard for IoT messaging
  - Topic hierarchy design (e.g., `factory/{area}/{machine}/{metric}`)
  - QoS levels (0=at most once, 1=at least once, 2=exactly once)
  - Retained messages for state
- **OPC-UA**: Industrial automation standard
- **Modbus/Profinet**: Direct PLC communication

**For Service Layer (Backend Services)**:
- **REST APIs**: Synchronous request-response
- **gRPC**: High-performance RPC
- **Message Queue**: Asynchronous event-driven
- **WebSockets**: Real-time bidirectional

**Your Task**: Design topic hierarchies, API endpoints, and message schemas.

### 5. Containerization & Orchestration

**Decision**: How are services packaged and deployed?

**Docker Containerization**:
- Container per service (simulation engine, API server, database)
- Base images (Python, Node.js, official databases)
- Multi-stage builds for optimization
- Docker Compose for local development

**Kubernetes Orchestration**:
- Deployments for stateless services
- StatefulSets for databases
- Services for discovery and load balancing
- ConfigMaps and Secrets for configuration
- Horizontal Pod Autoscaling
- Persistent Volumes for data

**Your Task**: Design Kubernetes manifest structure and resource allocation.

### 6. Security & Reliability

**Decision**: How is the system secured and made resilient?

**Security Considerations**:
- Authentication & Authorization (OAuth2, JWT, RBAC)
- TLS/SSL encryption for all communication
- Secrets management (Kubernetes Secrets, HashiCorp Vault)
- Network policies and firewalls
- Input validation and sanitization
- Audit logging

**Reliability Considerations**:
- Redundancy (multiple broker instances, database replicas)
- Health checks and automatic restart
- Graceful degradation (edge autonomy during cloud outage)
- Backup and disaster recovery
- Monitoring and alerting (Prometheus + Grafana)

**Your Task**: Specify security measures and failure handling strategies.

---

## Design Document Structure

Your 8-10 page design document should follow this structure:

### 1. Executive Summary (0.5 pages)

Brief overview of the system, its purpose, and key architectural decisions.

### 2. System Overview (1 page)

- Description of the physical system being modeled
- Business objectives and key performance indicators (KPIs)
- Scope and boundaries of the Digital Twin
- High-level architecture diagram reference

### 3. Dimension 1: Physical Entity (1 page)

- Sensor inventory (types, locations, sampling rates)
- Actuator capabilities and control interfaces
- Edge device specifications and roles
- Industrial communication protocols
- Time synchronization strategy
- Physical safety requirements

### 4. Dimension 2: Virtual Entity (1.5 pages)

- Simulation paradigm selection and justification
- Model architecture and components
- Parameterization and calibration approach
- State estimation methodology
- Uncertainty quantification strategy
- Model validation approach
- Predictive capabilities (scenarios supported)

### 5. Dimension 3: Data (1 page)

- Data taxonomy (telemetry, events, commands, KPIs)
- Data schemas and formats
- Database technology selection (time-series, relational, document)
- Data volume estimates and storage planning
- Data quality and validation procedures
- Data retention and archival policies
- Privacy and compliance considerations

### 6. Dimension 4: Connection (1.5 pages)

- Network topology (edge, cloud, hybrid)
- MQTT architecture:
  - Broker deployment (single, clustered, bridged)
  - Topic hierarchy design with examples
  - QoS level selection per topic type
- API design:
  - REST endpoint structure
  - Request/response schemas
  - Authentication mechanisms
- Latency budgets for critical paths
- Bandwidth requirements and optimization
- Failure modes and recovery mechanisms

### 7. Dimension 5: Services (2 pages)

- Service decomposition (microservices breakdown)
- Service responsibilities and interfaces
- Technology stack per service (languages, frameworks)
- Service communication patterns
- Deployment architecture:
  - Docker containerization strategy
  - Kubernetes resource specifications
  - Scaling policies (HPA configuration)
  - Cloud vs. edge placement decisions
- Monitoring and observability (Prometheus, Grafana, logging)
- Security architecture (authentication, authorization, encryption)

### 8. Deployment & Operations (0.5 pages)

- CI/CD pipeline overview
- Environment management (dev, staging, production)
- Rollout and rollback strategies
- Monitoring and alerting strategy
- Backup and disaster recovery

### 9. Alternative Designs Considered (0.5 pages)

- Brief discussion of alternative architectural approaches
- Trade-offs that led to your chosen design
- Future evolution possibilities

### 10. Conclusion (0.5 pages)

- Summary of key architectural decisions
- Expected benefits and capabilities
- Known limitations and mitigation strategies

---

## Technical Specifications

### MQTT Topic Hierarchy Example

For the Hybrid Factory Model, design a topic structure like:

```
factory/
├── production/
│   ├── line1/
│   │   ├── machine/status          # {idle, busy, down}
│   │   ├── machine/health          # 0.0-1.0
│   │   ├── queue/length            # integer
│   │   └── production/count        # cumulative
│   └── line2/...
├── maintenance/
│   ├── technicians/tech1/status    # {idle, walking, repairing}
│   ├── technicians/tech1/location  # {x, y}
│   └── requests/queue              # JSON array
├── simulation/
│   ├── state/sync                  # periodic state snapshot
│   ├── prediction/scenarios        # scenario results
│   └── optimization/recommendations
└── control/
    ├── commands/maintenance        # dispatch technician
    └── commands/production         # adjust production rate
```

**QoS Levels**:
- Sensor telemetry: QoS 0 (best effort, high frequency)
- Status changes: QoS 1 (at least once)
- Control commands: QoS 2 (exactly once, critical)

### Microservices Decomposition Example

**Core Services**:

1. **Data Ingestion Service**
   - Language: Go (high throughput)
   - Subscribes to MQTT sensor topics
   - Validates and normalizes data
   - Writes to time-series database
   - Publishes to message queue for processing

2. **Simulation Service**
   - Language: Python (SimPy, NumPy, SciPy)
   - Runs digital twin simulation
   - Consumes state updates from message queue
   - Publishes predictions to MQTT
   - Exposes REST API for scenario requests

3. **State Estimation Service**
   - Language: Python (NumPy, SciPy)
   - Kalman filtering for state synchronization
   - Fuses sensor data with model predictions
   - Publishes corrected state estimates

4. **Optimization Service**
   - Language: Python (SciPy, OR-Tools)
   - Runs simulation-based optimization
   - Generates operational recommendations
   - Scheduled jobs + on-demand API

5. **API Gateway**
   - Language: Node.js or Go
   - Kong or Traefik
   - Handles authentication
   - Routes requests to backend services
   - Rate limiting and caching

6. **Dashboard Service**
   - Language: JavaScript (React/Vue)
   - WebSocket connection for real-time updates
   - Visualizes KPIs and predictions
   - Operator control interface

7. **Database Services**
   - TimescaleDB (time-series data)
   - PostgreSQL (relational data)
   - Redis (caching, session)

8. **Message Broker**
   - MQTT Broker (Mosquitto or EMQX)
   - RabbitMQ or Kafka (internal queuing)

### Docker Compose Example Structure

```yaml
services:
  mqtt-broker:
    image: eclipse-mosquitto:2.0
    ports: [1883:1883, 9001:9001]
    volumes: [./mosquitto.conf:/mosquitto/config/mosquitto.conf]

  timescaledb:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: [tsdb-data:/var/lib/postgresql/data]

  data-ingestion:
    build: ./services/data-ingestion
    depends_on: [mqtt-broker, timescaledb]
    environment:
      MQTT_BROKER: mqtt-broker:1883
      DATABASE_URL: postgresql://timescaledb:5432/factory

  simulation:
    build: ./services/simulation
    depends_on: [mqtt-broker, timescaledb]
    environment:
      MQTT_BROKER: mqtt-broker:1883
    deploy:
      replicas: 3

  api-gateway:
    image: kong:3.4
    ports: [8000:8000, 8001:8001]
    depends_on: [postgres]

  dashboard:
    build: ./services/dashboard
    ports: [3000:3000]
    depends_on: [api-gateway]

  grafana:
    image: grafana/grafana:10.0
    ports: [3001:3000]
    volumes: [grafana-data:/var/lib/grafana]

volumes:
  tsdb-data:
  grafana-data:
```

### Kubernetes Deployment Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simulation-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: simulation
  template:
    metadata:
      labels:
        app: simulation
    spec:
      containers:
      - name: simulation
        image: factory-dt/simulation:v1.0
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
        env:
        - name: MQTT_BROKER
          value: "mqtt-service:1883"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: simulation-service
spec:
  selector:
    app: simulation
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: simulation-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: simulation-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Evaluation Rubric

Your project will be evaluated on the following criteria (see RUBRIC.md for detailed breakdown):

| Criterion | Weight | Key Aspects |
|-----------|--------|-------------|
| **Architectural Completeness** | 25% | All 5 dimensions addressed comprehensively |
| **Technical Depth** | 25% | Detailed specifications, technology justifications |
| **Design Quality** | 20% | Clarity, feasibility, scalability, best practices |
| **Documentation Quality** | 15% | Professional writing, clear diagrams, organization |
| **Decision Justification** | 10% | Trade-off analysis, alternatives considered |
| **Innovation & Creativity** | 5% | Novel solutions, advanced techniques |

**Total**: 100 points

---

## Submission Requirements

### File Structure

Submit a single ZIP file named `LastName_FirstName_DigitalTwinArchitecture.zip` containing:

```
LastName_FirstName_DigitalTwinArchitecture/
├── README.md                          # Project overview
├── architecture_diagram.pdf           # or .png (high resolution)
├── design_document.pdf                # Main deliverable (8-10 pages)
├── technical_appendix/                # Optional: detailed specs
│   ├── mqtt_topic_hierarchy.md
│   ├── api_specifications.yaml
│   ├── docker-compose.example.yml
│   ├── kubernetes_manifests/
│   └── database_schemas.sql
└── references.md                      # Citations and resources
```

### Document Formatting

- **Font**: Professional (Arial, Calibri, Times New Roman)
- **Size**: 11-12pt body text
- **Spacing**: 1.15-1.5 line spacing
- **Margins**: 1 inch all sides
- **Page Limit**: 8-10 pages (excluding diagrams, which may be separate)
- **Headers/Footers**: Include page numbers, your name, date
- **Diagrams**: High resolution, readable when printed
- **Code Snippets**: Monospace font, syntax highlighting optional

### Submission Deadline

**Due Date**: [To be announced by instructor]

**Late Policy**: [To be specified by instructor]

---

## Resources and References

### Recommended Reading

- **Digital Twin Concepts**:
  - Grieves, M. (2014). "Digital Twin: Manufacturing Excellence through Virtual Factory Replication"
  - Tao, F. et al. (2018). "Digital Twin in Industry: State-of-the-Art"

- **MQTT and IoT**:
  - MQTT Version 5.0 Specification: https://mqtt.org/
  - "MQTT Essentials" series by HiveMQ

- **Microservices Architecture**:
  - Newman, S. (2021). "Building Microservices" (2nd Edition)
  - Richardson, C. "Microservices Patterns"

- **Kubernetes**:
  - "Kubernetes in Action" by Marko Lukša
  - Official Kubernetes Documentation: https://kubernetes.io/docs/

### Technology Documentation

- **SimPy**: https://simpy.readthedocs.io/
- **TimescaleDB**: https://docs.timescale.com/
- **Mosquitto MQTT**: https://mosquitto.org/documentation/
- **Docker**: https://docs.docker.com/
- **Kubernetes**: https://kubernetes.io/docs/
- **Prometheus & Grafana**: https://prometheus.io/docs/, https://grafana.com/docs/

### Tools for Diagramming

- **draw.io**: https://app.diagrams.net/ (free, web-based)
- **Lucidchart**: https://www.lucidchart.com/ (free tier available)
- **PlantUML**: https://plantuml.com/ (code-based diagrams)
- **Mermaid**: https://mermaid.js.org/ (markdown-compatible diagrams)

---

## Frequently Asked Questions

**Q: Can I work in a team?**
A: [To be specified by instructor - typically individual project]

**Q: Can I use a different system instead of the Hybrid Factory Model?**
A: Yes, with instructor approval. Your alternative system must meet the complexity requirements listed in "System Selection" section.

**Q: Do I need to implement the system?**
A: No. This is a design project. You create the blueprint, not the implementation. However, small code snippets (MQTT topic examples, API schemas, Docker configs) enhance your documentation.

**Q: How detailed should the architectural diagram be?**
A: It should show all major components, their relationships, data flows, and technology choices. Someone should be able to understand the entire system architecture from your diagram alone.

**Q: Can I use cloud services (AWS, Azure, GCP)?**
A: Yes, you may specify cloud services. Clearly indicate which components run on cloud vs. edge, and justify the cost/benefit trade-off.

**Q: What if I don't have experience with Kubernetes?**
A: You should research and learn the basics. Part of this project is demonstrating your ability to learn new technologies. Use the provided resources and examples.

**Q: How do I show trade-off analysis?**
A: In your design document, include an "Alternatives Considered" section where you discuss other approaches (e.g., "We considered a monolithic architecture but chose microservices because...") and explain your reasoning.

**Q: Can I get feedback before the final submission?**
A: [To be specified by instructor - office hours, draft reviews, etc.]

---

## Academic Integrity

This is an individual project. While you may discuss general concepts with classmates, your design and documentation must be your own original work. Properly cite any external resources, frameworks, or architectural patterns you reference.

**Prohibited**:
- Copying design documents from online sources
- Sharing architectural diagrams with classmates
- Using AI to write significant portions of your document (AI for brainstorming/outlining is acceptable with disclosure)

**Acceptable**:
- Referencing industry best practices and design patterns (with citation)
- Using standard architectural templates and frameworks
- Consulting official technology documentation
- Discussing general concepts in study groups

---

## Getting Started Checklist

- [ ] Review all 11 previous labs, especially Lab 8 (Hybrid Factory Model)
- [ ] Read Chapter 14 of the course textbook
- [ ] Choose your system (recommended: Hybrid Factory Model)
- [ ] Create initial architectural sketch (rough draft)
- [ ] Research technology choices (MQTT brokers, databases, orchestration)
- [ ] Outline your design document using the provided structure
- [ ] Create detailed architectural diagram
- [ ] Write design document sections incrementally
- [ ] Review evaluation rubric and self-assess
- [ ] Proofread and format document professionally
- [ ] Prepare submission ZIP file
- [ ] Submit before deadline

---

## Conclusion

This capstone project represents the integration of everything you've learned in this course. You've built simulations using multiple paradigms, implemented state estimation, created predictive scenario analysis, and applied optimization techniques. Now you'll synthesize this knowledge into a production-ready architectural design.

This is your opportunity to demonstrate not just technical skills, but also systems thinking, engineering judgment, and professional communication. Take this seriously—the skills you develop here are directly applicable to real-world Digital Twin projects in industry.

**Good luck!**

---

*For questions or clarifications, contact the instructor during office hours or via email.*
