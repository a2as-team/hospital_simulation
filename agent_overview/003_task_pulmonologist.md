# Task for Pulmonologist Office: Building a Modern CrewAI Medical Scheduling Assistant

This is an updated guide to creating a pulmonologist office scheduling assistant using CrewAI. This version uses a more modern, class-based approach that is better organized, more reusable, and aligns with the latest CrewAI practices.

## 1. Goal: A Modern, Reusable Medical Scheduling Agent

We will build a self-contained `PulmonologistSchedulingAgent` class. This class will handle everything: initializing the AI model, defining the agent and its tools, and running the tasks. This is a much cleaner pattern than having loose functions.

**Core Concepts in this Approach:**

*   **Agent Class:** A Python class (`PulmonologistSchedulingAgent`) that encapsulates all the logic for our medical scheduling assistant.
*   **Class-Based Tool:** A robust way to create tools by inheriting from `BaseTool` and defining a `pydantic` model for the arguments. This provides structure, type safety, and clarity.
*   **`invoke` Method:** A single, clear entry point to make the agent perform its task.
*   **`crewai.LLM`:** The native CrewAI way to configure and use language models like Gemini.

## 2. Setting Up Your Environment

Let's get your project set up.

**Prerequisites:**

*   Python version 3.10 or newer.

**Installation:**

1.  **Create a project directory and a virtual environment:**

    ```bash
    mkdir pulmonologist-scheduling-agent
    cd pulmonologist-scheduling-agent
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install the necessary packages:**

    From the root of the project (`a2a-medical-coordinator`), you can now install the Pulmonologist agent and all its dependencies with a single command:
    ```bash
    pip install -e a2a_medical_coordinator/pulmonologist_agent_crewai
    ```
    This tells `pip` to install the `pulmonologist-scheduling-agent` package in "editable" (`-e`) mode, which is great for development.

3.  **Set up your Gemini API key:**

    Navigate to the `a2a_medical_coordinator/pulmonologist_agent_crewai` directory and create a file named `.env`.

    ```.env
    GOOGLE_API_KEY="your-google-api-key"
    ```

    You can get your key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## 3. Building the Medical Scheduling Agent Class

Below is the complete, runnable Python script. Save this as `agent.py`. It implements the full `PulmonologistSchedulingAgent` using the modern, class-based approach with a well-defined tool.

```python
import os
import random
from datetime import date, datetime, timedelta
from typing import Type

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


def generate_appointment_schedule() -> dict[str, list[str]]:
    """Generates a random appointment schedule for the next 7 days."""
    schedule = {}
    today = date.today()
    possible_times = [f"{h:02}:00" for h in range(8, 17)]  # 8 AM to 5 PM (medical office hours)

    for i in range(7):
        current_date = today + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        available_slots = sorted(random.sample(possible_times, 6))  # 6 available slots per day
        schedule[date_str] = available_slots
    print("---- Pulmonologist's Generated Schedule ----")
    print(schedule)
    print("------------------------------------------")
    return schedule


PULMONOLOGIST_SCHEDULE = generate_appointment_schedule()


class AppointmentAvailabilityInput(BaseModel):
    """Input schema for AppointmentAvailabilityTool."""

    date_range: str = Field(
        ...,
        description="The date or date range to check for appointment availability, e.g., '2024-07-28' or '2024-07-28 to 2024-07-30'.",
    )


class AppointmentAvailabilityTool(BaseTool):
    name: str = "Pulmonologist Appointment Availability Checker"
    description: str = (
        "Checks the pulmonologist's appointment availability for a given date or date range. "
        "Use this to find out when appointment slots are available."
    )
    args_schema: Type[BaseModel] = AppointmentAvailabilityInput

    def _run(self, date_range: str) -> str:
        """Checks appointment availability for a given date range."""
        dates_to_check = [d.strip() for d in date_range.split("to")]
        start_date_str = dates_to_check[0]
        end_date_str = dates_to_check[-1]

        try:
            start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start > end:
                return "Invalid date range. The start date cannot be after the end date."

            results = []
            delta = end - start
            for i in range(delta.days + 1):
                day = start + timedelta(days=i)
                date_str = day.strftime("%Y-%m-%d")
                available_slots = PULMONOLOGIST_SCHEDULE.get(date_str, [])
                if available_slots:
                    availability = f"On {date_str}, the pulmonologist has available appointment slots at: {', '.join(available_slots)}."
                    results.append(availability)
                else:
                    results.append(f"No appointment slots available on {date_str}.")

            return "\n".join(results)

        except ValueError:
            return (
                "I couldn't understand the date. "
                "Please provide appointment availability request for a date like 'YYYY-MM-DD'."
            )


class PulmonologistSchedulingAgent:
    """Agent that handles pulmonologist appointment scheduling tasks."""

    def __init__(self):
        """Initializes the PulmonologistSchedulingAgent."""
        if os.getenv("GOOGLE_API_KEY"):
            self.llm = LLM(
                model="gemini/gemini-1.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY"),
            )
        else:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")

        self.appointment_scheduler = Agent(
            role="Pulmonologist Office Scheduling Assistant",
            goal="Check the pulmonologist's appointment schedule and answer questions about appointment availability.",
            backstory=(
                "You are a highly efficient and professional medical office assistant. Your only job is "
                "to manage the pulmonologist's appointment schedule. You are an expert at using the "
                "Pulmonologist Appointment Availability Checker tool to find out when appointment slots are available. "
                "You maintain strict professionalism and only engage in conversations related to medical appointment scheduling."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[AppointmentAvailabilityTool()],
            llm=self.llm,
        )

    def invoke(self, question: str) -> str:
        """Kicks off the crew to answer an appointment scheduling question."""
        task_description = (
            f"Answer the user's question about pulmonologist appointment availability. The user asked: '{question}'. "
            f"Today's date is {date.today().strftime('%Y-%m-%d')}."
        )

        check_appointment_availability_task = Task(
            description=task_description,
            expected_output="A polite and professional answer to the user's question about pulmonologist appointment availability, based on the appointment scheduling tool's output.",
            agent=self.appointment_scheduler,
        )

        crew = Crew(
            agents=[self.appointment_scheduler],
            tasks=[check_appointment_availability_task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff()
        return str(result)


if __name__ == "__main__":
    user_question = "Do you have any appointment slots available tomorrow?"
    scheduling_agent = PulmonologistSchedulingAgent()
    result = scheduling_agent.invoke(user_question)

    print("\n\n######################")
    print("## Here is the result")
    print("######################\n")
    print(result)
```

## 4. How to Run Your Agent

With your `agent.py` and `.env` files in place, run the script from your terminal:

```bash
python agent.py
```

This will instantiate your `SchedulingAgent` class and call its `invoke` method, kicking off the crew to answer the question.

## 5. Key Benefits of This Approach

*   **Encapsulation:** All the logic related to the agent is contained within a single class, making it easy to understand, manage, and import elsewhere in a larger medical application.
*   **Structured Tools:** Defining an `args_schema` with Pydantic ensures that the agent provides the correct arguments to your tool, reducing runtime errors.
*   **Clarity and Reusability:** This pattern makes the agent's capabilities and entry point clear and explicit, and the `PulmonologistSchedulingAgent` class can be easily reused.

This structure provides a robust foundation for building more complex and powerful medical scheduling CrewAI agents.
