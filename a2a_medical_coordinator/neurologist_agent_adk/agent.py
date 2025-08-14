import random
from datetime import date, datetime, timedelta
from typing import Dict, List

from google.adk.agents import LlmAgent

# Medical office configuration
NEUROLOGY_OFFICE_CONFIG = {
    'office_hours_start': 8,  # 8 AM
    'office_hours_end': 17,   # 5 PM  
    'slots_per_day': 6,       # Available appointment slots per day
    'schedule_days_ahead': 7  # Generate schedule for next 7 days
}


def initialize_neurologist_appointment_schedule() -> Dict[str, List[str]]:
    """Initialize the neurologist's appointment schedule for the upcoming week."""
    appointment_schedule = {}
    current_date = date.today()
    
    # Generate hourly time slots during office hours
    office_time_slots = [
        f"{hour:02d}:00" 
        for hour in range(
            NEUROLOGY_OFFICE_CONFIG['office_hours_start'], 
            NEUROLOGY_OFFICE_CONFIG['office_hours_end']
        )
    ]

    # Create schedule for each day
    for day_offset in range(NEUROLOGY_OFFICE_CONFIG['schedule_days_ahead']):
        schedule_date = current_date + timedelta(days=day_offset)
        date_key = schedule_date.strftime("%Y-%m-%d")
        
        # Randomly select available appointment slots for the day
        available_appointment_slots = sorted(
            random.sample(office_time_slots, NEUROLOGY_OFFICE_CONFIG['slots_per_day'])
        )
        appointment_schedule[date_key] = available_appointment_slots

    print(f"Neurologist office appointment schedule initialized: {appointment_schedule}")
    return appointment_schedule


# Global schedule instance
NEUROLOGIST_APPOINTMENT_SCHEDULE = initialize_neurologist_appointment_schedule()


def check_neurologist_appointment_availability(
    requested_start_date: str, 
    requested_end_date: str
) -> str:
    """
    Query the neurologist's appointment availability within a specified date range.

    Args:
        requested_start_date: Start of the date range to check, in YYYY-MM-DD format.
        requested_end_date: End of the date range to check, in YYYY-MM-DD format.

    Returns:
        Formatted string containing available appointment slots for the date range.
    """
    try:
        # Parse and validate date inputs
        start_date_obj = datetime.strptime(requested_start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(requested_end_date, "%Y-%m-%d").date()

        # Validate date range logic
        if start_date_obj > end_date_obj:
            return "Error: Start date cannot be after end date. Please provide a valid date range."

        # Check if dates are in the past
        today = date.today()
        if end_date_obj < today:
            return "Error: Cannot check availability for past dates. Please provide future dates."

        availability_results = []
        date_range_delta = end_date_obj - start_date_obj

        # Check each day in the requested range
        for day_offset in range(date_range_delta.days + 1):
            check_date = start_date_obj + timedelta(days=day_offset)
            date_string = check_date.strftime("%Y-%m-%d")
            
            available_time_slots = NEUROLOGIST_APPOINTMENT_SCHEDULE.get(date_string, [])
            
            if available_time_slots:
                day_availability = (
                    f"📅 {date_string}: Neurologist available at "
                    f"{', '.join(available_time_slots)} for consultations."
                )
                availability_results.append(day_availability)
            else:
                availability_results.append(
                    f"📅 {date_string}: No neurologist appointment slots available."
                )

        return "\n".join(availability_results) if availability_results else "No availability data found."

    except ValueError:
        return (
            "Error: Invalid date format detected. Please use YYYY-MM-DD format "
            "for both start and end dates (e.g., 2024-03-15)."
        )


def create_neurologist_scheduling_agent() -> LlmAgent:
    """Create and configure the neurologist office scheduling agent."""
    return LlmAgent(
        model="gemini-2.5-flash-preview-04-17",
        name="Neurologist_Office_Agent",
        instruction="""
            **Professional Role:** You are the official appointment scheduling assistant for the Neurologist's office. 
            Your primary responsibility is managing the neurologist's appointment calendar and providing accurate 
            availability information to patients and referring physicians.

            **Core Responsibilities:**

            *   **Appointment Availability Queries:** Use the `check_neurologist_appointment_availability` tool to 
                    verify available appointment slots for requested dates. The tool requires both a start_date 
                    and end_date parameter. For single-day requests, use the same date for both parameters.
                    
            *   **Professional Communication Standards:** 
                    - Maintain a courteous, professional medical office tone
                    - Provide clear, concise responses with specific time slots
                    - Use appropriate medical office terminology
                    - Include relevant appointment details when available
                    
            *   **Scope Limitations:** 
                    - Only handle neurologist appointment scheduling inquiries
                    - Politely redirect non-scheduling questions with: "I can only assist with neurologist 
                      appointment scheduling. Please contact our main office for other inquiries."
                    - Do not provide medical advice or discuss treatment options
                    
            **Response Format:** Always format availability responses clearly with dates and specific time slots.
        """,
        tools=[check_neurologist_appointment_availability],
    )
