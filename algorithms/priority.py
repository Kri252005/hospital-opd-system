def calculate_priority_score(patient_data):
    """
    Calculate priority score (0-100, higher = more urgent)
    
    Args:
        patient_data (dict): {
            'is_emergency': bool,
            'symptom_severity': str,
            'age': int,
            'has_chronic_condition': bool,
            'visit_type': str
        }
    
    Returns:
        float: priority_score
    """
    score = 0
    
    # 1. Emergency Status (40 points)
    if patient_data.get('is_emergency', False):
        score += 40
    
    # 2. Symptom Severity (30 points)
    severity_mapping = {
        'Critical': 30,
        'High': 20,
        'Moderate': 10,
        'Low': 5
    }
    score += severity_mapping.get(patient_data.get('symptom_severity', 'Moderate'), 10)
    
    # 3. Age-based Priority (15 points)
    age = patient_data.get('age', 30)
    if age >= 70:
        score += 15
    elif age >= 60:
        score += 10
    elif age <= 5:
        score += 12
    elif age <= 12:
        score += 8
    
    # 4. Chronic Conditions (10 points)
    if patient_data.get('has_chronic_condition', False):
        score += 10
    
    # 5. Visit Type (5 points)
    visit_type_mapping = {
        'Emergency': 5,
        'Follow-up': 3,
        'Appointment': 2,
        'Walk-in': 0
    }
    score += visit_type_mapping.get(patient_data.get('visit_type', 'Walk-in'), 0)
    
    return min(score, 100)  # Cap at 100


def test_priority_calculation():
    """Test function to verify priority calculation"""
    test_cases = [
        {
            'name': 'Emergency Critical Patient',
            'data': {
                'is_emergency': True,
                'symptom_severity': 'Critical',
                'age': 75,
                'has_chronic_condition': True,
                'visit_type': 'Emergency'
            },
            'expected': 100
        },
        {
            'name': 'Regular Walk-in',
            'data': {
                'is_emergency': False,
                'symptom_severity': 'Moderate',
                'age': 35,
                'has_chronic_condition': False,
                'visit_type': 'Walk-in'
            },
            'expected': 10
        }
    ]
    
    for test in test_cases:
        score = calculate_priority_score(test['data'])
        print(f"{test['name']}: {score} (Expected: {test['expected']})")

# Run test
if __name__ == '__main__':
    test_priority_calculation()