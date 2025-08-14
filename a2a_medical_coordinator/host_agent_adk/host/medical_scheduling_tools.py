from datetime import date, datetime, timedelta
from typing import Dict, Optional
import uuid

# In-memory database for medical appointment schedules
# Maps date strings to dictionaries of time slots and patient information
MEDICAL_APPOINTMENT_SCHEDULE: Dict[str, Dict[str, str]] = {}

# Medical office configuration
OFFICE_HOURS = {
    'start_hour': 8,  # 8 AM
    'end_hour': 17,   # 5 PM
    'appointment_duration': 1  # 1 hour slots
}


def initialize_medical_schedule():
    """Initialize the medical appointment schedule for the next 7 days."""
    global MEDICAL_APPOINTMENT_SCHEDULE
    current_date = date.today()
    
    available_time_slots = [
        f"{hour:02d}:00" 
        for hour in range(OFFICE_HOURS['start_hour'], OFFICE_HOURS['end_hour'])
    ]

    for day_offset in range(7):
        schedule_date = current_date + timedelta(days=day_offset)
        date_key = schedule_date.strftime("%Y-%m-%d")
        MEDICAL_APPOINTMENT_SCHEDULE[date_key] = {
            time_slot: "available" for time_slot in available_time_slots
        }


# Initialize the schedule when the module is loaded
initialize_medical_schedule()


def list_appointment_availabilities(appointment_date: str) -> dict:
    """
    Retrieve available and booked appointment slots for a specific date.

    Args:
        appointment_date: The date to check availability for, in YYYY-MM-DD format.

    Returns:
        A dictionary containing the status, message, and detailed schedule information.
    """
    # Validate date format
    try:
        parsed_date = datetime.strptime(appointment_date, "%Y-%m-%d")
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid date format. Please provide date in YYYY-MM-DD format.",
            "error_code": "INVALID_DATE_FORMAT"
        }

    # Check if date is in the past
    if parsed_date.date() < date.today():
        return {
            "status": "error",
            "message": f"Cannot check availability for past date: {appointment_date}",
            "error_code": "PAST_DATE_NOT_ALLOWED"
        }

    daily_appointment_schedule = MEDICAL_APPOINTMENT_SCHEDULE.get(appointment_date)
    if not daily_appointment_schedule:
        return {
            "status": "success",
            "message": f"No appointment slots configured for {appointment_date}.",
            "available_slots": [],
            "booked_appointments": {},
            "total_slots": 0
        }

    available_time_slots = [
        time_slot for time_slot, booking_status in daily_appointment_schedule.items() 
        if booking_status == "available"
    ]
    
    booked_appointments = {
        time_slot: patient_info 
        for time_slot, patient_info in daily_appointment_schedule.items() 
        if patient_info != "available"
    }

    return {
        "status": "success",
        "message": f"Medical appointment schedule for {appointment_date}.",
        "available_slots": available_time_slots,
        "booked_appointments": booked_appointments,
        "total_slots": len(daily_appointment_schedule),
        "available_count": len(available_time_slots),
        "booked_count": len(booked_appointments)
    }


def book_medical_appointment(
    appointment_date: str, 
    start_time: str, 
    end_time: str, 
    patient_name: str,
    appointment_type: Optional[str] = "consultation"
) -> dict:
    """
    Book a medical appointment for a patient on a specific date and time.

    Args:
        appointment_date: The date of the appointment, in YYYY-MM-DD format.
        start_time: The start time of the appointment, in HH:MM format.
        end_time: The end time of the appointment, in HH:MM format.
        patient_name: The name of the patient for the appointment.
        appointment_type: Type of appointment (default: "consultation").

    Returns:
        A dictionary with booking confirmation or error details.
    """
    # Validate input parameters
    if not patient_name or not patient_name.strip():
        return {
            "status": "error",
            "message": "Patient name is required to book an appointment.",
            "error_code": "MISSING_PATIENT_NAME"
        }

    # Validate date and time formats
    try:
        appointment_start = datetime.strptime(f"{appointment_date} {start_time}", "%Y-%m-%d %H:%M")
        appointment_end = datetime.strptime(f"{appointment_date} {end_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time.",
            "error_code": "INVALID_DATETIME_FORMAT"
        }

    # Validate appointment duration
    if appointment_start >= appointment_end:
        return {
            "status": "error", 
            "message": "Appointment start time must be before end time.",
            "error_code": "INVALID_TIME_RANGE"
        }

    # Check if appointment date exists in schedule
    if appointment_date not in MEDICAL_APPOINTMENT_SCHEDULE:
        return {
            "status": "error", 
            "message": f"No appointment slots available on {appointment_date}.",
            "error_code": "DATE_NOT_AVAILABLE"
        }

    # Calculate required time slots
    required_time_slots = []
    current_slot_time = appointment_start
    while current_slot_time < appointment_end:
        required_time_slots.append(current_slot_time.strftime("%H:%M"))
        current_slot_time += timedelta(hours=OFFICE_HOURS['appointment_duration'])

    # Check availability of all required slots
    daily_schedule = MEDICAL_APPOINTMENT_SCHEDULE.get(appointment_date, {})
    for time_slot in required_time_slots:
        if daily_schedule.get(time_slot, "booked") != "available":
            existing_patient = daily_schedule.get(time_slot, "unknown patient")
            return {
                "status": "error",
                "message": f"Appointment slot {time_slot} on {appointment_date} is already booked for {existing_patient}.",
                "error_code": "SLOT_ALREADY_BOOKED",
                "conflicting_slot": time_slot,
                "existing_patient": existing_patient
            }

    # Book all required slots
    appointment_id = str(uuid.uuid4())[:8]  # Generate short appointment ID
    patient_booking_info = f"{patient_name} ({appointment_type})"
    
    for time_slot in required_time_slots:
        MEDICAL_APPOINTMENT_SCHEDULE[appointment_date][time_slot] = patient_booking_info

    return {
        "status": "success",
        "message": f"Medical appointment successfully booked for {patient_name}.",
        "appointment_details": {
            "appointment_id": appointment_id,
            "patient_name": patient_name,
            "appointment_type": appointment_type,
            "date": appointment_date,
            "start_time": start_time,
            "end_time": end_time,
            "duration_hours": len(required_time_slots),
            "booked_slots": required_time_slots
        }
    }
