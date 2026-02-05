USE hospital_opd;

-- Table 1: Patients
CREATE TABLE patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('M', 'F', 'Other') NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    blood_group VARCHAR(5),
    chronic_conditions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_registration (registration_number)
);

-- Table 2: Departments
CREATE TABLE departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL,
    department_code VARCHAR(10) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: Doctors
CREATE TABLE doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    doctor_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    average_consultation_time INT DEFAULT 10,
    is_available BOOLEAN DEFAULT TRUE,
    current_status ENUM('Available', 'Busy', 'On_Break', 'Offline') DEFAULT 'Available',
    max_patients_per_session INT DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    INDEX idx_availability (is_available, current_status)
);

-- Table 4: Queue Entries
CREATE TABLE queue_entries (
    queue_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    department_id INT NOT NULL,
    token_number VARCHAR(20) NOT NULL,
    visit_type ENUM('Walk-in', 'Appointment', 'Follow-up', 'Emergency') NOT NULL,
    age INT NOT NULL,
    symptom_severity ENUM('Low', 'Moderate', 'High', 'Critical') DEFAULT 'Moderate',
    has_chronic_condition BOOLEAN DEFAULT FALSE,
    is_emergency BOOLEAN DEFAULT FALSE,
    priority_score DECIMAL(5,2) NOT NULL,
    queue_position INT,
    status ENUM('Waiting', 'In_Progress', 'Completed', 'Cancelled') DEFAULT 'Waiting',
    check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    consultation_start_time TIMESTAMP NULL,
    consultation_end_time TIMESTAMP NULL,
    estimated_wait_time INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    INDEX idx_queue_status (doctor_id, status, priority_score DESC)
);

-- Table 5: Consultation History
CREATE TABLE consultation_history (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    queue_id INT NOT NULL,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    actual_consultation_time INT,
    consultation_notes TEXT,
    diagnosis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (queue_id) REFERENCES queue_entries(queue_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- Table 6: System Events
CREATE TABLE system_events (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    event_type ENUM('Check-in', 'Consultation_Start', 'Consultation_End', 
                    'Emergency_Arrival', 'Doctor_Status_Change') NOT NULL,
    queue_id INT,
    doctor_id INT,
    event_data JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);