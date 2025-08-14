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
                return (
                    "Invalid date range. The start date cannot be after the end date."
                )

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

    SUPPORTED_CONTENT_TYPES = ["text/plain"]

    def __init__(self):
        """Initializes the PulmonologistSchedulingAgent."""
        if os.getenv("GOOGLE_API_KEY"):
            self.llm = LLM(
                model="gemini/gemini-2.0-flash",
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
