from models.database import execute_query
from algorithms.priority import calculate_priority_score
from datetime import datetime

def reorder_queue(doctor_id):
    """
    Reorder waiting patients for a specific doctor
    
    Args:
        doctor_id (int): Doctor's ID
    
    Returns:
        list: Updated queue
    """
    # Get all waiting patients
    query = """
        SELECT queue_id, priority_score, check_in_time, is_emergency
        FROM queue_entries
        WHERE doctor_id = %s AND status = 'Waiting'
        ORDER BY is_emergency DESC, 
                 priority_score DESC, 
                 check_in_time ASC
    """
    
    waiting_patients = execute_query(query, (doctor_id,), fetch=True)
    
    # Assign new positions
    for position, patient in enumerate(waiting_patients, start=1):
        update_query = """
            UPDATE queue_entries
            SET queue_position = %s, updated_at = NOW()
            WHERE queue_id = %s
        """
        execute_query(update_query, (position, patient['queue_id']))
    
    print(f"✅ Queue reordered for Doctor {doctor_id}: {len(waiting_patients)} patients")
    return waiting_patients


def generate_token(department_id):
    """
    Generate unique token number like CARD-001
    
    Args:
        department_id (int): Department ID
    
    Returns:
        str: Token number
    """
    # Get department code
    dept_query = "SELECT department_code FROM departments WHERE department_id = %s"
    dept = execute_query(dept_query, (department_id,), fetch=True)
    
    if not dept:
        raise ValueError(f"Department {department_id} not found")
    
    dept_code = dept[0]['department_code']
    
    # Count today's patients for this department
    count_query = """
        SELECT COUNT(*) as cnt 
        FROM queue_entries
        WHERE department_id = %s 
        AND DATE(check_in_time) = CURDATE()
    """
    count_result = execute_query(count_query, (department_id,), fetch=True)
    count = count_result[0]['cnt'] if count_result else 0
    
    # Format: CARD-001, CARD-002, etc.
    token = f"{dept_code}-{str(count + 1).zfill(3)}"
    return token


def get_queue_position(queue_id):
    """Get current queue position for a patient"""
    query = "SELECT queue_position FROM queue_entries WHERE queue_id = %s"
    result = execute_query(query, (queue_id,), fetch=True)
    return result[0]['queue_position'] if result else None