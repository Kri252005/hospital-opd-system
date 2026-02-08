from flask import Blueprint, request, jsonify
from models.database import execute_query
from algorithms.wait_time import recalculate_wait_times
from datetime import datetime

bp = Blueprint('doctor', __name__)

@bp.route('/<int:doctor_id>/queue', methods=['GET'])
def get_doctor_queue(doctor_id):
    """Get all waiting patients for a doctor"""
    try:
        query = """
            SELECT 
                q.queue_id, q.token_number, q.queue_position,
                q.priority_score, q.estimated_wait_time, q.symptom_severity,
                q.is_emergency, q.notes,
                p.first_name, p.last_name, p.age, p.chronic_conditions
            FROM queue_entries q
            JOIN patients p ON q.patient_id = p.patient_id
            WHERE q.doctor_id = %s AND q.status = 'Waiting'
            ORDER BY q.queue_position ASC
        """
        queue = execute_query(query, (doctor_id,), fetch=True)
        
        return jsonify({
            'success': True,
            'total_waiting': len(queue),
            'queue': queue
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:doctor_id>/current', methods=['GET'])
def get_current_patient(doctor_id):
    """Get patient currently being consulted"""
    try:
        query = """
            SELECT 
                q.*, 
                p.first_name, p.last_name, p.phone, p.chronic_conditions,
                TIMESTAMPDIFF(MINUTE, q.consultation_start_time, NOW()) as elapsed_time
            FROM queue_entries q
            JOIN patients p ON q.patient_id = p.patient_id
            WHERE q.doctor_id = %s AND q.status = 'In_Progress'
            LIMIT 1
        """
        result = execute_query(query, (doctor_id,), fetch=True)
        
        if not result:
            return jsonify({'message': 'No patient in consultation'}), 200
        
        return jsonify(result[0]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:doctor_id>/start-consultation', methods=['POST'])
def start_consultation(doctor_id):
    """
    Start consultation with next patient
    
    Expected JSON:
    {
        "queue_id": 123
    }
    """
    try:
        data = request.json
        queue_id = data.get('queue_id')
        
        if not queue_id:
            return jsonify({'error': 'queue_id required'}), 400
        
        # Update queue entry
        update_queue = """
            UPDATE queue_entries
            SET status = 'In_Progress', 
                consultation_start_time = NOW()
            WHERE queue_id = %s AND doctor_id = %s
        """
        execute_query(update_queue, (queue_id, doctor_id))
        
        # Update doctor status
        update_doctor = """
            UPDATE doctors
            SET current_status = 'Busy'
            WHERE doctor_id = %s
        """
        execute_query(update_doctor, (doctor_id,))
        
        # Recalculate wait times
        recalculate_wait_times(doctor_id)
        
        # Log event
        log_query = """
            INSERT INTO system_events (event_type, queue_id, doctor_id)
            VALUES ('Consultation_Start', %s, %s)
        """
        execute_query(log_query, (queue_id, doctor_id))
        
        return jsonify({
            'success': True,
            'message': 'Consultation started'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:doctor_id>/end-consultation', methods=['POST'])
def end_consultation(doctor_id):
    """
    End current consultation
    
    Expected JSON:
    {
        "queue_id": 123,
        "diagnosis": "Common cold",
        "notes": "Prescribed rest and fluids"
    }
    """
    try:
        data = request.json
        queue_id = data.get('queue_id')
        
        # Mark consultation complete
        update_query = """
            UPDATE queue_entries
            SET status = 'Completed',
                consultation_end_time = NOW()
            WHERE queue_id = %s
        """
        execute_query(update_query, (queue_id,))
        
        # Calculate actual consultation time
        time_query = """
            SELECT 
                patient_id,
                TIMESTAMPDIFF(MINUTE, consultation_start_time, consultation_end_time) as duration
            FROM queue_entries WHERE queue_id = %s
        """
        time_result = execute_query(time_query, (queue_id,), fetch=True)
        actual_time = time_result[0]['duration']
        patient_id = time_result[0]['patient_id']
        
        # Save to history
        history_query = """
            INSERT INTO consultation_history 
            (queue_id, patient_id, doctor_id, actual_consultation_time, 
             consultation_notes, diagnosis)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        execute_query(history_query, (
            queue_id, patient_id, doctor_id, actual_time,
            data.get('notes', ''), data.get('diagnosis', '')
        ))
        
        # Update doctor's average consultation time
        avg_query = """
            UPDATE doctors
            SET average_consultation_time = (
                SELECT AVG(actual_consultation_time)
                FROM consultation_history
                WHERE doctor_id = %s
            )
            WHERE doctor_id = %s
        """
        execute_query(avg_query, (doctor_id, doctor_id))
        
        # Set doctor as available
        status_query = """
            UPDATE doctors
            SET current_status = 'Available'
            WHERE doctor_id = %s
        """
        execute_query(status_query, (doctor_id,))
        
        # Get next patient
        next_query = """
            SELECT queue_id, token_number
            FROM queue_entries
            WHERE doctor_id = %s AND status = 'Waiting'
            ORDER BY queue_position ASC
            LIMIT 1
        """
        next_patient = execute_query(next_query, (doctor_id,), fetch=True)
        
        # Log event
        log_query = """
            INSERT INTO system_events (event_type, queue_id, doctor_id)
            VALUES ('Consultation_End', %s, %s)
        """
        execute_query(log_query, (queue_id, doctor_id))
        
        return jsonify({
            'success': True,
            'consultation_time': actual_time,
            'next_patient': next_patient[0] if next_patient else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500