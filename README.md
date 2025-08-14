# A2A Medical Appointment Coordinator
This document describes a multi-agent application demonstrating how to orchestrate conversations between different agents to schedule medical appointments.

This application contains four agents:
*   **Host Agent**: The primary agent that orchestrates the appointment scheduling task.
*   **Cardiologist Agent**: An agent representing the Cardiologist office's calendar and availability.
*   **Pulmonologist Agent**: An agent representing the Pulmonologist office's calendar and availability.
*   **Neurologist Agent**: An agent representing the Neurologist office's calendar and availability.

## Setup and Deployment

### Prerequisites

Before running the application locally, ensure you have the following installed:

1. **uv:** The Python package management tool used in this project. Follow the installation guide: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
2. **python 3.13** Python 3.13 is required to run a2a-sdk 
3. **set up .env** 

Create a `.env` file in the root of the `a2a_medical_coordinator` directory with your Google API Key:
```
GOOGLE_API_KEY="your_api_key_here" 
```

## Run the Agents

You will need to run each agent in a separate terminal window. The first time you run these commands, `uv` will create a virtual environment and install all necessary dependencies before starting the agent.

### Terminal 1: Run Cardiologist Agent
```bash
cd cardiologist_agent_langgraph
uv venv
source .venv/bin/activate
uv run --active app/__main__.py
```

### Terminal 2: Run Pulmonologist Agent
```bash
cd pulmonologist_agent_crewai
uv venv
source .venv/bin/activate
uv run --active .
```

### Terminal 3: Run Neurologist Agent
```bash
cd neurologist_agent_adk
uv venv
source .venv/bin/activate
uv run --active .
```

### Terminal 4: Run Host Agent
```bash
cd host_agent_adk
uv venv
source .venv/bin/activate
uv run --active adk web      
```

## Interact with the Host Agent

Once all agents are running, the host agent will begin the appointment scheduling process. You can view the interaction in the terminal output of the `host_agent`.

