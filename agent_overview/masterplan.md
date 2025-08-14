# Medical Appointment Coordination System
## Agent-to-Agent Multi-Specialist Scheduling Platform

### 1. Project Overview

This project implements a sophisticated multi-agent system designed to streamline medical appointment coordination between patients and specialist healthcare providers. The system demonstrates advanced Agent-to-Agent (A2A) communication protocols, where autonomous agents built with diverse frameworks collaborate seamlessly to achieve optimal appointment scheduling outcomes.

#### Key Objectives:
- **Automated Coordination**: Eliminate manual scheduling bottlenecks
- **Multi-Specialist Integration**: Coordinate across different medical specialties
- **Framework Diversity**: Showcase interoperability between different AI frameworks
- **Patient-Centric Experience**: Provide seamless appointment booking experience

### 2. System Architecture

The architecture follows a hub-and-spoke model with a central coordination agent managing communication with multiple specialist office agents.

#### Core Components:

**🏥 Central Coordination Layer**
-   **Medical Appointment Coordinator (Host Agent)**: Central orchestrator built with ADK
-   **ADK Web Interface**: Patient-facing web application for appointment requests
-   **Communication Hub**: Manages A2A protocol messaging between all agents

**🩺 Specialist Office Agents**
Each specialist office operates an autonomous agent responsible for:
- Managing appointment calendars and availability
- Processing appointment requests and confirmations  
- Maintaining patient scheduling preferences
- Coordinating with the central system

#### Communication Flow:
```
Patient Request → Host Agent → Specialist Agents → Availability Check → Appointment Booking → Confirmation
```

1. **Patient Initiation**: Patient submits appointment request via web interface
2. **Request Processing**: Host Agent analyzes requirements and identifies relevant specialists
3. **Availability Query**: Parallel queries sent to appropriate specialist office agents
4. **Response Aggregation**: Host Agent consolidates availability responses
5. **Appointment Booking**: Confirmed time slots are reserved across systems
6. **Patient Notification**: Final confirmation sent to patient with appointment details

### 3. Agent Ecosystem

The system comprises four specialized agents, each running as independent microservices with dedicated APIs for seamless inter-agent communication.

#### 3.1. Medical Appointment Coordinator (Host Agent)
**🎯 Primary Orchestrator**

| Attribute | Details |
|-----------|---------|
| **Framework** | Agent Development Kit (ADK) |
| **Primary Role** | Central appointment coordination and patient request management |
| **Key Responsibilities** | • Patient request processing<br>• Multi-specialist coordination<br>• Appointment conflict resolution<br>• Patient communication management |
| **Network Port** | `10001` |
| **Status** | ✅ Core functionality implemented, optimization in progress |

#### 3.2. Specialist Office Agent Network

Each specialist office operates an autonomous agent with unique capabilities and scheduling patterns.

##### 3.2.1. 🧠 Neurologist Office Agent
| Attribute | Details |
|-----------|---------|
| **Framework** | Agent Development Kit (ADK) |
| **Medical Specialty** | Neurology consultations and diagnostics |
| **Scheduling Pattern** | Standard business hours with emergency slots |
| **Integration Model** | Direct ADK-to-ADK communication |
| **Network Port** | `10002` |
| **Unique Features** | • Specialized neurological assessment scheduling<br>• Emergency consultation availability<br>• Follow-up appointment automation |

##### 3.2.2. 🫁 Pulmonologist Office Agent  
| Attribute | Details |
|-----------|---------|
| **Framework** | CrewAI |
| **Medical Specialty** | Respiratory and pulmonary care |
| **Scheduling Pattern** | Extended consultation slots for complex cases |
| **Integration Model** | CrewAI-to-ADK bridge communication |
| **Network Port** | `10003` |
| **Unique Features** | • Respiratory function test coordination<br>• Multi-session treatment planning<br>• Specialist equipment scheduling |

##### 3.2.3. ❤️ Cardiologist Office Agent
| Attribute | Details |
|-----------|---------|
| **Framework** | LangGraph |
| **Medical Specialty** | Cardiovascular diagnostics and treatment |
| **Scheduling Pattern** | Flexible scheduling with urgent care prioritization |
| **Integration Model** | LangGraph-to-ADK workflow integration |
| **Network Port** | `10004` |
| **Unique Features** | • Cardiac procedure scheduling<br>• Pre-operative consultation management<br>• Emergency cardiac care coordination |

### 4. Medical Scheduling Infrastructure

#### 4.1. Advanced Scheduling Tools Suite

The Host Agent leverages a comprehensive toolkit designed specifically for medical appointment coordination:

**🔍 Specialist Availability Engine**
- **Multi-Agent Query System**: Parallel availability checks across all specialist agents
- **Real-time Availability Sync**: Live updates from specialist office systems
- **Conflict Detection**: Automatic identification of scheduling conflicts
- **Priority-based Scheduling**: Urgent care and emergency appointment prioritization

**📅 Intelligent Appointment Matching**
- **Patient Preference Analysis**: Considers patient scheduling preferences and constraints
- **Specialist Expertise Matching**: Routes patients to appropriate specialists based on medical needs
- **Optimal Time Slot Selection**: AI-driven selection of best available appointment times
- **Multi-appointment Coordination**: Manages complex cases requiring multiple specialist visits

**💾 Appointment Booking Engine**
- **Atomic Booking Operations**: Ensures data consistency across all systems
- **Confirmation Workflow**: Multi-step confirmation process with all parties
- **Cancellation Management**: Handles appointment modifications and cancellations
- **Waitlist Management**: Automatic patient notification for earlier available slots

#### 4.2. Data Management Architecture

**📊 Appointment Database Schema**
```sql
-- Core appointment tracking table
appointments (
    appointment_id UUID PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL,
    specialist_type VARCHAR(100) NOT NULL,
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    appointment_type VARCHAR(100) DEFAULT 'consultation',
    status VARCHAR(50) DEFAULT 'scheduled',
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Specialist availability tracking
specialist_availability (
    availability_id UUID PRIMARY KEY,
    specialist_agent VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    time_slot TIME NOT NULL,
    status VARCHAR(50) DEFAULT 'available',
    reserved_for VARCHAR(255),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**🗄️ Technology Stack**
- **Primary Database**: SQLite for development, PostgreSQL for production
- **Caching Layer**: Redis for high-frequency availability queries  
- **Backup Strategy**: Automated daily backups with point-in-time recovery
- **Data Encryption**: At-rest and in-transit encryption for patient data protection

## 5. Development Plan

1.  **Finalize Master Plan:** Flesh out this document with any more details.
2.  **Develop Medical Appointment Scheduling Tools:** Create the Python scripts for the appointment scheduling tools, including the SQLite database interaction.
3.  **Review and Refine Host Agent:** Correct the "raw instructions" for the host agent and integrate the new medical scheduling tools.
4.  **Develop Neurologist Office Agent (ADK):** Create the agent and expose it as a server.
5.  **Develop Pulmonologist Office Agent (CrewAI):** Create the agent and expose it as a server.
6.  **Develop Cardiologist Office Agent (LangGraph):** Create the agent and expose it as a server.
7.  **Integration and Testing:** Ensure all agents can communicate with the host agent and a medical appointment can be successfully scheduled.
