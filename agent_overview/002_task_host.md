# Task: Refactor the Host Agent

This document outlines the plan for refactoring the `host` agent (previously the `RoutingAgent`) to act as the central orchestrator for scheduling medical appointments with specialist office agents.

## 1. Project Structure and Naming

-   **Directory Cleanup:** The agent's code currently resides in `a2a_medical_coordinator/host_agent/host`. To simplify, move the contents of the inner `host` directory (`agent.py`, `remote_agent_connection.py`, etc.) up into `host_agent` and delete the now-empty `host` folder.
-   **Rename `host_agent` to `host`:** Rename the top-level `host_agent` directory to just `host` for consistency with the other agent directories (`neurologist_agent`, etc.).
-   **Rename `RoutingAgent`:** The class `RoutingAgent` in `agent.py` should be renamed to `HostAgent` to more accurately reflect its new role.

## 2. Develop Medical Appointment Scheduling Tools

A new set of tools is required for the Host Agent to manage the appointment scheduling process. These will be created in a new file: `host/medical_scheduling_tools.py`.

-   **Database Setup (`db.py`):**
    -   Create a file `host/db.py` to manage the SQLite database connection.
    -   It will include functions to initialize the database and create an `appointments` table with columns for `id`, `datetime`, `specialist_name`, `patient_name`, and `appointment_type`.
-   **Medical Scheduling Tools (`medical_scheduling_tools.py`):**
    -   **`check_specialists_availability`:** This tool will take a list of specialist names and a proposed date. It will use the `send_message` function to query each specialist's agent for their availability on that date.
    -   **`find_common_appointment_slots`:** This tool will process the availability responses from the specialist agents and identify available appointment slots.
    -   **`book_medical_appointment`:** This tool will take a confirmed time, date, specialist, and patient information, and it will create an appointment reservation in the SQLite database.

## 3. Refactor the Host Agent (`agent.py`)

-   **Update Initialization:**
    -   Modify the `create` method to accept a list of specialist agent URLs from environment variables (e.g., `NEUROLOGIST_AGENT_URL`, `PULMONOLOGIST_AGENT_URL`, `CARDIOLOGIST_AGENT_URL`). It should be configured to connect to all three specialist agents, not just a single hardcoded one.
-   **Update Instructions:**
    -   Completely rewrite the `root_instruction` method. The new instructions will guide the agent on its role as a medical appointment coordinator.
    -   It should direct the agent to first use `check_specialists_availability`, then `find_common_appointment_slots`, and finally `book_medical_appointment`.
-   **Integrate Tools:**
    -   The `create_agent` method must be updated to include the new medical scheduling tools in its `tools` list, alongside the existing `send_message` tool.

## 4. Create a Server Entry Point (`__main__.py`)

-   The host agent currently lacks a standalone server entry point.
-   Create a new file, `host/__main__.py`, that is responsible for:
    -   Loading environment variables.
    -   Instantiating the `HostAgent`.
    -   Running the agent as an A2A server on its designated port, `10001`.
    -   This file will be similar in structure to `neurologist_agent/__main__.py`.
