from flask import Blueprint, request, jsonify
from models.database import execute_query
from algorithms.priority import calculate_priority_score
from algorithms.queue_manager import reorder_queue, generate_token
from algorithms.wait_time import estimate_wait_time
from datetime import datetime

bp = Blueprint('patient', __name__)

@bp.route('/checkin', methods=['POST'])
def check_in_patient():
    """
    Patient check-in endpoint
    
    Expected JSON:
    {
        "patient_id": 1,
        "doctor_id": 1,
        "department_id": 1,
        "visit_type": "Walk-in",
        "symptom_severity": "Moderate",
        "is_emergency": false,
        "notes": "Chest pain"
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required = ['patient_id', 'doctor_id', 'department_id', 'visit_type']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Get patient age and chronic conditions
        patient_query = """
            SELECT 
                TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) as age,
                chronic_conditions
            FROM patients
            WHERE patient_id = %s
        """
        patient_info = execute_query(patient_query, (data['patient_id'],), fetch=True)
        
        if not patient_info:
            return jsonify({'error': 'Patient not found'}), 404
        
        age = patient_info[0]['age']
        chronic_conditions = patient_info[0]['chronic_conditions']
        has_chronic = len(chronic_conditions) > 0 if chronic_conditions else False
        
        # Calculate priority score
        priority_data = {
            'is_emergency': data.get('is_emergency', False),
            'symptom_severity': data.get('symptom_severity', 'Moderate'),
            'age': age,
            'has_chronic_condition': has_chronic,
            'visit_type': data['visit_type']
        }
        priority_score = calculate_priority_score(priority_data)
        
        # Generate token
        token = generate_token(data['department_id'])
        
        # Insert into queue
        insert_query = """
            INSERT INTO queue_entries 
            (patient_id, doctor_id, department_id, token_number, visit_type,
             age, symptom_severity, has_chronic_condition, is_emergency,
             priority_score, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Waiting', %s)
        """
        
        queue_id = execute_query(insert_query, (
            data['patient_id'],
            data['doctor_id'],
            data['department_id'],
            token,
            data['visit_type'],
            age,
            data.get('symptom_severity', 'Moderate'),
            has_chronic,
            data.get('is_emergency', False),
            priority_score,
            data.get('notes', '')
        ))
        
        # Reorder queue
        reorder_queue(data['doctor_id'])
        
        # Estimate wait time
        wait_time = estimate_wait_time(queue_id)
        
        # Get queue position
        position_query = "SELECT queue_position FROM queue_entries WHERE queue_id = %s"
        position_result = execute_query(position_query, (queue_id,), fetch=True)
        queue_position = position_result[0]['queue_position']
        
        # Log event
        log_query = """
            INSERT INTO system_events (event_type, queue_id, doctor_id)
            VALUES ('Check-in', %s, %s)
        """
        execute_query(log_query, (queue_id, data['doctor_id']))
        
        return jsonify({
            'success': True,
            'queue_id': queue_id,
            'token_number': token,
            'priority_score': float(priority_score),
            'queue_position': queue_position,
            'estimated_wait_time': wait_time,
            'message': f'Checked in successfully. Token: {token}'
        }), 201
        
    except Exception as e:
        print(f"❌ Check-in error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/queue-status/<int:queue_id>', methods=['GET'])
def get_queue_status(queue_id):
    """Get current status of a patient in queue"""
    try:
        query = """
            SELECT 
                q.token_number, q.queue_position, q.estimated_wait_time,
                q.status, q.priority_score,
                p.first_name, p.last_name,
                d.doctor_name
            FROM queue_entries q
            JOIN patients p ON q.patient_id = p.patient_id
            JOIN doctors d ON q.doctor_id = d.doctor_id
            WHERE q.queue_id = %s
        """
        result = execute_query(query, (queue_id,), fetch=True)
        
        if not result:
            return jsonify({'error': 'Queue entry not found'}), 404
        
        return jsonify(result[0]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500