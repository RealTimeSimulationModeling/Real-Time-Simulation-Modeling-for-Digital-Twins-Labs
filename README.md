# Real-Time Simulation Modeling for Digital Twins

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![SimPy](https://img.shields.io/badge/SimPy-4.0+-green.svg)](https://simpy.readthedocs.io/)

**A comprehensive, hands-on laboratory curriculum for building Digital Twin systems**

---

## Overview

This repository contains complete educational materials for **IDS 6742: Real-Time Simulation Modeling for Digital Twins**, a graduate-level course that teaches students to design, implement, and deploy Digital Twin systems from first principles to production architecture.

### What You'll Learn

- **Multiple simulation paradigms**: Discrete Event Simulation (DES), Agent-Based Modeling (ABM), System Dynamics (SD), and physics-based ODEs
- **Real-time integration**: MQTT communication, sensor data streaming, bidirectional control
- **State estimation**: Kalman filtering, sensor fusion, uncertainty quantification
- **Predictive analytics**: Scenario analysis, Monte Carlo simulation, confidence intervals
- **Optimization**: Simulation-based optimization, prescriptive analytics
- **Production deployment**: Microservices architecture, Docker, Kubernetes
- **Professional ethics**: Privacy, bias, accountability in AI-driven systems

### Why This Curriculum?

Digital Twin development requires interdisciplinary skills rarely taught together. This curriculum:

- **Integrates** simulation, IoT, state estimation, and optimization in coherent projects
- **Builds progressively** from simple queues to production architectures
- **Teaches first principles** before frameworks (understand what tools do for you)
- **Pairs technical skills with ethical reasoning** for complete engineering education

---

## Course Structure

### Phase 1: Foundations (Labs 1-5)

Master individual simulation paradigms in isolation.

| Lab | Title | Paradigm | Key Concepts |
|-----|-------|----------|--------------|
| **1** | First Python Simulation | Manual DES | Loops, state variables, exponential arrivals |
| **2** | Coffee Shop with SimPy | DES | Process-based modeling, resources, queues |
| **3** | Warehouse AGVs | ABM | Autonomous agents, emergent behavior, coordination |
| **4** | Workforce Dynamics | SD | Stocks, flows, feedback loops, Euler integration |
| **5** | DC Motor Control | ODE | Physics-based modeling, scipy.integrate |

### Phase 2: Integration (Labs 6-8)

Connect simulations with real-time data and combine paradigms.

| Lab | Title | Focus | Key Concepts |
|-----|-------|-------|--------------|
| **6** | MQTT Data Link | IoT Communication | Pub/sub, topics, QoS, JSON messages |
| **7** | Kalman Filter State Sync | State Estimation | Predict-update cycle, sensor fusion |
| **8** | Hybrid Factory Model | Multi-Paradigm | DES+ABM+SD integration, cross-paradigm events |

### Phase 3: Advanced Analytics (Labs 9-11)

Build predictive and prescriptive capabilities.

| Lab | Title | Focus | Key Concepts |
|-----|-------|-------|--------------|
| **9** | Continuous Validation | Parameter Learning | PI controller recalibration, Monte Carlo UQ |
| **10** | Predictive Scenarios | What-If Analysis | State forking, FTRT clones, KPI comparison |
| **11** | Simulation Optimization | Prescriptive Analytics | Differential evolution, stochastic objectives |

### Phase 4: Synthesis (Lab 12, Session 13)

Design production systems and reflect on responsibility.

| Module | Title | Focus | Deliverable |
|--------|-------|-------|-------------|
| **12** | Capstone Architecture | Production Design | Diagram + 8-10 page design document |

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Basic programming knowledge (loops, functions, classes)
- Familiarity with command line

### Installation

```bash
# Clone the repository
git clone https://github.com/RealTimeSimulationModeling/Real-Time-Simulation-Modeling-for-Digital-Twins-Labs.git
cd Real-Time-Simulation-Modeling4Digital-Twins-Labs

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Your First Simulation

```bash
# Navigate to Lab 1
cd Lab1-First-Python-Simulation

# Run the coffee shop simulation
python coffee_shop_sim.py
```

**Expected Output**:
```
--- Simulating 100 Customers ---

==================================================
           SIMULATION RESULTS
==================================================

Performance Metrics:
  Average Wait Time:      3.42 minutes
  Maximum Wait Time:      15.23 minutes
  Probability of Waiting: 68.00%
  Server Utilization:     87.12%
  Average Time in System: 6.89 minutes
==================================================
```

### Explore the Labs

Each lab folder contains:
- `README.md` - Overview and learning objectives
- `LAB_GUIDE.md` - Comprehensive instructions (when applicable)
- `QUICKSTART.md` - Fast path to running code
- `*.py` - Python implementations (solution + starter template)
- `requirements.txt` - Lab-specific dependencies

---

## Repository Structure

```
Real-Time-Simulation-Modeling4Digital-Twins-Labs/
│
├── Lab1-First-Python-Simulation/       # Manual DES implementation
│   ├── coffee_shop_sim.py              # Complete solution
│   ├── coffee_shop_sim_starter.py      # Student template
│   ├── LAB_GUIDE.md                    # Comprehensive guide
│   ├── QUICKSTART.md                   # 10-minute path
│   └── README.md                       # Overview
│
├── Lab2-Coffee-Shop-DES/               # SimPy introduction
├── Lab3-Warehouse-AGV-ABM/             # Agent-based modeling
├── Lab4-Workforce-System-Dynamics/     # Stock-and-flow models
├── Lab5-DC-Motor-ODE/                  # Physics-based simulation
├── Lab6-MQTT-Data-Link/                # IoT communication
├── Lab7-Kalman-Filter-State-Sync/      # State estimation
├── Lab8-Hybrid-Factory-Model/          # Multi-paradigm integration
├── Lab9-Continuous-Validation/         # Parameter learning & UQ
├── Lab10-Predictive-Scenarios/         # What-if analysis
├── Lab11-Simulation-Optimization/      # Prescriptive analytics
├── Lab12-Capstone-Digital-Twin-Architecture/
│   ├── PROJECT_SPECIFICATION.md        # Complete requirements
│   ├── DESIGN_TEMPLATE.md              # Document template
│   ├── RUBRIC.md                       # 100-point evaluation
│   ├── QUICKSTART.md                   # Week-by-week guide
│   └── README.md                       # Project overview
│
├── requirements.txt                    # Global dependencies
├── LICENSE                             # MIT License
└── README.md                           # This file
```

---

## Technical Requirements

### Core Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| Python | ≥3.8 | Core language |
| SimPy | ≥4.0.1 | Discrete event simulation |
| NumPy | ≥1.21.0 | Numerical computing |
| SciPy | ≥1.7.0 | Optimization, ODEs, statistics |
| Matplotlib | ≥3.5.0 | Visualization |
| Paho-MQTT | ≥1.6.0 | MQTT communication |

### Installation

```bash
pip install simpy numpy scipy matplotlib paho-mqtt
```

Or use the provided requirements file:

```bash
pip install -r requirements.txt
```

### Optional Dependencies

For Lab 12 (architecture design), students should be familiar with:
- Docker and Docker Compose
- Kubernetes concepts
- MQTT brokers (Mosquitto, EMQX)
- Time-series databases (TimescaleDB, InfluxDB)

---

## Learning Path

### Recommended Sequence

**Weeks 1-2**: Labs 1-2 (DES Foundations)
- Understand event-driven simulation
- Learn SimPy's process-based paradigm

**Weeks 3-4**: Labs 3-4 (ABM and SD)
- Model autonomous agents
- Understand feedback loops

**Week 5**: Lab 5 (Physics-Based Modeling)
- Solve ODEs with scipy
- Model electromechanical systems

**Weeks 6-7**: Labs 6-7 (Real-Time Integration)
- Implement MQTT communication
- Apply Kalman filtering

**Week 8**: Lab 8 (Hybrid Modeling)
- Integrate DES + ABM + SD
- Design cross-paradigm interactions

**Weeks 9-11**: Labs 9-11 (Advanced Analytics)
- Parameter recalibration
- Scenario analysis
- Optimization

**Weeks 12**: Lab 12 (Capstone)
- Design production architecture


### Time Commitment

| Component | Estimated Hours |
|-----------|-----------------|
| Lab 1 (foundation) | 3-4 hours |
| Labs 2-7 | 2-3 hours each |
| Lab 8 (hybrid) | 4-5 hours |
| Labs 9-11 | 3-4 hours each |
| Lab 12 (capstone) | 25-35 hours |
| **Total** | **~75 hours** |

---

## Key Results and Metrics

### Simulation Performance

| Lab | System | Key Metric | Typical Value |
|-----|--------|------------|---------------|
| 1-2 | Coffee Shop | Avg Wait Time | 3.4 min |
| 3 | Warehouse AGVs | Tasks/8hr | 127 |
| 5 | DC Motor | Settling Time | 0.89 s |
| 7 | Kalman Filter | RMS Error Reduction | 78.5% |
| 8 | Hybrid Factory | Parts/Shift | 89 |
| 9 | Parameter Est. | Convergence Error | <0.2% |
| 11 | Optimization | Cost Reduction | 41.8% |

### Learning Outcomes

Upon completion, students can:

1. **Model** complex systems with appropriate paradigms
2. **Implement** real-time data integration via MQTT
3. **Apply** Kalman filtering for state estimation
4. **Conduct** predictive scenario analysis with UQ
5. **Perform** simulation-based optimization
6. **Design** production-ready DT architectures
7. **Evaluate** ethical implications of DT applications

---

## For Instructors

### Adopting This Curriculum

All materials are designed for immediate classroom use:

- **Complete implementations**: Working code for all labs
- **Starter templates**: Guided TODOs for student exercises
- **Comprehensive guides**: Theory + instructions + experiments
- **Assessment rubrics**: Clear grading criteria
- **Ethics materials**: Session plan + student prep + evaluation

### Customization Options

- **Adjust difficulty**: Use starter templates (easier) or problem statements (harder)
- **Change systems**: Swap coffee shop for healthcare queue, factory for supply chain
- **Add hardware**: Integrate Raspberry Pi sensors for Labs 6-7
- **Extend optimization**: Add machine learning surrogate models


---

## For Self-Learners

### Where to Start

1. **Complete beginner**: Start with Lab 1 (no frameworks, just Python)
2. **Know Python**: Start with Lab 2 (SimPy introduction)
3. **Know simulation**: Jump to Lab 6 (real-time integration)
4. **Want architecture**: Start with Lab 12 docs (design patterns)

### Learning Tips

- **Run before reading**: Execute the code first, then study it
- **Experiment**: Change parameters and observe effects
- **Break things**: Intentionally cause errors to understand mechanics
- **Complete exercises**: Don't skip the analysis questions
- **Connect concepts**: Each lab builds on previous ones

### Community Support

- **Issues**: Report bugs or ask questions via GitHub Issues
- **Discussions**: Share adaptations and improvements
- **Pull Requests**: Contribute enhancements

---

## Citation

If you use these materials in your research or teaching, please cite:

```bibtex
@misc{digitaltwin_curriculum_bulent_soykan,
  title={Real-Time Simulation Modeling for Digital Twins: Laboratory Curriculum},
  author={Bulent Soykan},
  year={2026},
  howpublished={\url{https://github.com/RealTimeSimulationModeling/Real-Time-Simulation-Modeling-for-Digital-Twins-Labs}},
  note={IDS 6742 Course Materials}
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**You are free to**:
- Use these materials for teaching
- Modify and adapt for your context
- Share with attribution

---

## Acknowledgments

- **SimPy Team**: For excellent DES framework and documentation
- **NumPy/SciPy Communities**: For robust scientific computing tools
- **Eclipse Mosquitto**: For reliable MQTT broker
- **Students**: For feedback that improved these materials

---

## Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Bug fixes**: Submit PR with description of issue and fix
2. **Enhancements**: Open issue first to discuss
3. **New labs**: Propose via issue with learning objectives
4. **Documentation**: Always appreciated!

---

## Roadmap

### Planned Enhancements

- [ ] **Hardware integration**: Raspberry Pi + sensors for Labs 6-7
- [ ] **Cloud deployment**: Actually deploy Lab 12 on Kubernetes
- [ ] **ML module**: Lab on machine learning surrogate models
- [ ] **Video tutorials**: Walkthrough videos for each lab
- [ ] **Industry cases**: Real-world case studies from partners

### Version History

- **v1.0** (Jan 2026): Initial release with 12 labs + ethics session

---

## Contact

- **Course Website**: [University course page]
- **Issues**: GitHub Issues for bugs and questions
- **Email**: [Contact email]

---

## Quick Links

| Resource | Description |
|----------|-------------|
| [Lab 1: First Simulation](Lab1-First-Python-Simulation/) | Start here - manual DES |
| [Lab 8: Hybrid Factory](Lab8-Hybrid-Factory-Model/) | Multi-paradigm integration |
| [Lab 12: Capstone](Lab12-Capstone-Digital-Twin-Architecture/) | Architecture design project |

---

<p align="center">
  <b>Build Digital Twins. Understand the Technology. Question the Ethics.</b>
</p>

<p align="center">
  <i>From first principles to professional responsibility.</i>
</p>

---

**Happy Simulating!** 🏭🤖📊
