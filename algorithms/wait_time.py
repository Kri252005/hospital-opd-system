from models.database import execute_query
from datetime import datetime

def estimate_wait_time(queue_id):
    """
    Calculate estimated waiting time for a patient
    
    Args:
        queue_id (int): Queue entry ID
    
    Returns:
        int: Estimated wait time in minutes
    """
    # Get patient's queue details
    patient_query = """
        SELECT queue_position, doctor_id
        FROM queue_entries
        WHERE queue_id = %s
    """
    patient = execute_query(patient_query, (queue_id,), fetch=True)
    
    if not patient:
        return 0
    
    patient = patient[0]
    queue_position = patient['queue_position']
    doctor_id = patient['doctor_id']
    
    # Get doctor's average consultation time
    doctor_query = """
        SELECT average_consultation_time, current_status
        FROM doctors
        WHERE doctor_id = %s
    """
    doctor = execute_query(doctor_query, (doctor_id,), fetch=True)[0]
    avg_time = doctor['average_consultation_time']
    
    # Check if doctor is currently consulting
    current_query = """
        SELECT consultation_start_time
        FROM queue_entries
        WHERE doctor_id = %s AND status = 'In_Progress'
        ORDER BY consultation_start_time DESC
        LIMIT 1
    """
    current_patient = execute_query(current_query, (doctor_id,), fetch=True)
    
    wait_time = 0
    
    if current_patient:
        # Calculate remaining time for current consultation
        start_time = current_patient[0]['consultation_start_time']
        elapsed = (datetime.now() - start_time).total_seconds() / 60
        remaining = max(0, avg_time - elapsed)
        wait_time += remaining
    
    # Add time for patients ahead in queue
    patients_ahead = queue_position - 1
    wait_time += patients_ahead * avg_time
    
    # Update in database
    update_query = """
        UPDATE queue_entries
        SET estimated_wait_time = %s
        WHERE queue_id = %s
    """
    execute_query(update_query, (int(wait_time), queue_id))
    
    return int(wait_time)


def recalculate_wait_times(doctor_id):
    """Recalculate wait times for all waiting patients of a doctor"""
    query = """
        SELECT queue_id 
        FROM queue_entries
        WHERE doctor_id = %s AND status = 'Waiting'
    """
    patients = execute_query(query, (doctor_id,), fetch=True)
    
    for patient in patients:
        estimate_wait_time(patient['queue_id'])
    
    print(f"✅ Wait times recalculated for {len(patients)} patients")