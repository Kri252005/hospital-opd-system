# Test Scenarios

## Scenario 1: Normal Walk-in Patient
1. Open admin dashboard
2. Select patient "Ramesh Verma"
3. Select doctor "Dr. Rajesh Kumar"
4. Visit type: Walk-in
5. Severity: Moderate
6. Click Check-in
7. Verify token generated (CARD-001)
8. Verify patient appears in queue

## Scenario 2: Emergency Patient
1. Check-in patient with Emergency flag
2. Verify priority score >= 70
3. Verify patient moves to position #1

## Scenario 3: Multiple Patients - Priority Sorting
1. Check-in 5 patients with different severities
2. Verify queue ordered by priority
3. Check estimated wait times calculated correctly

## Scenario 4: Doctor Consultation Flow
1. Doctor starts consultation
2. Verify patient status = "In_Progress"
3. Doctor ends consultation
4. Verify next patient called
5. Verify wait times recalculated