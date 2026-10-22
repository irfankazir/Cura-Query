"""Create a tiny synthetic database for local demos. All records are fictional."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("hospital_patients.db")
sample_patients = [
    (1, "Alex Sample", 34, "Female", "O+", "Chennai", "alex.sample@example.com", "2025-01-12", "Flu", "Medication", "2025-01-16", "Dr. Example", 1200.00, "0000000001", "None"),
    (2, "Jordan Demo", 52, "Male", "A-", "Coimbatore", "jordan.demo@example.com", "2025-02-03", "Migraine", "Observation", "2025-02-05", "Dr. Sample", 850.00, "0000000002", "None"),
    (3, "Taylor Fiction", 27, "Female", "B+", "Madurai", "taylor.fiction@example.com", "2025-03-21", "Asthma", "Medication", "2025-03-25", "Dr. Example", 1600.00, "0000000003", "Allergy"),
    (4, "Casey Placeholder", 45, "Male", "AB+", "Salem", "casey.placeholder@example.com", "2025-04-08", "Fracture", "Physiotherapy", "2025-04-20", "Dr. Sample", 2400.00, "0000000004", "None"),
    (5, "Morgan Test", 61, "Female", "O-", "Trichy", "morgan.test@example.com", "2025-05-11", "Hypertension", "Medication", "2025-05-18", "Dr. Example", 1900.00, "0000000005", "Hypertension"),
]
schema = """CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY, name TEXT, age INTEGER, gender TEXT,
    blood_group TEXT, city TEXT, email TEXT, admission_date TEXT,
    diagnosis TEXT, treatment TEXT, discharge_date TEXT,
    doctor_assigned TEXT, bill_amount REAL, contact_number TEXT,
    medical_history TEXT
)"""
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("DROP TABLE IF EXISTS patients")
    conn.execute(schema)
    conn.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", sample_patients)
print(f"Created synthetic demo database: {DB_PATH}")
