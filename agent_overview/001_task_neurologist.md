# Task: Create Neurologist Office Agent

This document outlines the plan for creating the Neurologist office agent, which will be responsible for managing the neurologist's appointment schedule and responding to appointment booking requests. The agent will be built using the Agent Development Kit (ADK) and will be accessible to the Host Agent via the Agent-to-Agent (A2A) protocol.

This plan is based on the structure of the `@google_adk` sample project.

## 1. Project Setup

-   **Directory:** All files for the Neurologist agent will be located in the `a2a_medical_coordinator/neurologist_agent_adk/` directory.
-   **Dependencies:** Create a `pyproject.toml` file to manage the project's dependencies, including `a2a-google-adk`, `click`, `uvicorn`, and `python-dotenv`.

## 2. Agent Implementation

-   **`agent.py`:**
    -   Define a `NeurologistAgent` class.
    -   Define a `Tool` for checking the neurologist's appointment calendar. This will initially be a hardcoded schedule but can be replaced with a real medical scheduling system later.
    -   Implement the agent's core logic to process incoming appointment requests. The agent should be able to understand requests for availability and respond with open appointment slots.
    -   The agent's instructions will define its personality and capabilities, focusing on its role as a medical office scheduling assistant for the neurologist.

-   **`agent_executor.py`:**
    -   Create a `NeurologistAgentExecutor` class that inherits from `a2a.server.agent_execution.AgentExecutor`.
    -   This class will instantiate `NeurologistAgent`.
    -   It will implement the `execute` method to handle the lifecycle of an incoming appointment request, manage the task state (`working`, `input_required`, `failed`, `complete`), and stream responses back to the host.

-   **`__main__.py`:**
    -   This file will be the main entry point to run the agent as a server.
    -   It will use `click` to handle command-line arguments for `host` and `port`.
    -   It will define an `AgentCard` with metadata about the Neurologist agent (name, description, medical specialties, etc.).
    -   It will instantiate `NeurologistAgentExecutor`.
    -   It will set up and run a `A2AStarletteApplication` using `uvicorn`, passing it the `AgentCard` and a `DefaultRequestHandler` which in turn contains the `NeurologistAgentExecutor`. The server will run on port `10002`.

## 3. A2A Integration

-   The agent will be configured to communicate using the A2A protocol, allowing it to understand and respond to messages from the Host Agent.
-   The server will expose an endpoint that the Host Agent can call to interact with the Neurologist office agent.

## 4. Testing

-   Once the agent is running, we will test it by sending sample appointment requests to its endpoint to ensure it responds correctly with the neurologist's availability.
-   We will also test the integration with the Host Agent to confirm that they can communicate successfully.
