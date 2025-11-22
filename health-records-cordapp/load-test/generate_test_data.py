#!/usr/bin/env python3
"""
Generate random test data for Corda Health Records load testing
"""

import random
import json
import csv
from faker import Faker
import argparse
from collections import defaultdict
import os

fake = Faker()

# Medical data templates
VITAL_SIGNS = [
    ("Blood Pressure", lambda: f"{random.randint(90, 180)}/{random.randint(60, 120)} mmHg"),
    ("Heart Rate", lambda: f"{random.randint(50, 120)} bpm"),
    ("Temperature", lambda: f"{random.uniform(97.0, 102.0):.1f}°F"),
    ("Oxygen Saturation", lambda: f"{random.randint(90, 100)}%"),
    ("Weight", lambda: f"{random.randint(100, 300)} lbs"),
]

DIAGNOSES = [
    "Type 2 Diabetes Mellitus", "Hypertension Stage 1", "Hypertension Stage 2",
    "Hyperlipidemia", "Coronary Artery Disease", "Chronic Kidney Disease Stage 3",
    "Asthma", "COPD", "Osteoarthritis", "Depression",
]

MEDICATIONS = [
    "Metformin 500mg twice daily", "Lisinopril 10mg once daily",
    "Atorvastatin 20mg at bedtime", "Aspirin 81mg once daily",
    "Levothyroxine 50mcg once daily", "Omeprazole 20mg once daily",
]

LAB_TESTS = [
    ("HbA1c", lambda: f"{random.uniform(5.0, 12.0):.1f}%"),
    ("Fasting Blood Glucose", lambda: f"{random.randint(70, 250)} mg/dL"),
    ("Total Cholesterol", lambda: f"{random.randint(150, 300)} mg/dL"),
    ("Creatinine", lambda: f"{random.uniform(0.5, 2.5):.2f} mg/dL"),
]


def generate_patients(count):
    """Generate patient data"""
    return [{
        "patientId": f"P{i+1:06d}",
        "name": fake.name(),
        "age": random.randint(18, 90)
    } for i in range(count)]


def generate_medical_records(patient_id, count):
    """Generate medical records for a patient"""
    records = []
    
    # Vital signs (2-5 per patient)
    for _ in range(random.randint(2, 5)):
        vital_type, value_func = random.choice(VITAL_SIGNS)
        records.append({"patientId": patient_id, "title": vital_type, "value": value_func()})
    
    # Diagnosis (70% chance)
    if random.random() > 0.3:
        records.append({"patientId": patient_id, "title": "Diagnosis", "value": random.choice(DIAGNOSES)})
    
    # Medications (0-3 per patient)
    for _ in range(random.randint(0, 3)):
        records.append({"patientId": patient_id, "title": "Prescription", "value": random.choice(MEDICATIONS)})
    
    # Lab tests (1-4 per patient)
    for _ in range(random.randint(1, 4)):
        lab_type, value_func = random.choice(LAB_TESTS)
        records.append({"patientId": patient_id, "title": lab_type, "value": value_func()})
    
    return records[:count] if count else records


def save_data(data, filename, fieldnames=None):
    """Save data to JSON and CSV"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    # JSON
    with open(f"{filename}.json", 'w') as f:
        json.dump(data, f, indent=2)
    
    # CSV
    if fieldnames:
        with open(f"{filename}.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    print(f"✅ Saved {len(data)} records to {filename}.json/.csv")


def main():
    parser = argparse.ArgumentParser(description='Generate test data')
    parser.add_argument('--patients', type=int, default=1000, help='Number of patients')
    parser.add_argument('--records-per-patient', type=int, default=10, help='Records per patient')
    parser.add_argument('--output-dir', default='data', help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"📊 Generating {args.patients} patients...")
    patients = generate_patients(args.patients)
    
    print(f"📊 Generating medical records...")
    all_records = []
    for patient in patients:
        records = generate_medical_records(patient['patientId'], args.records_per_patient)
        all_records.extend(records)
    
    # Save files
    save_data(patients, f"{args.output_dir}/patients", ['patientId', 'name', 'age'])
    save_data(all_records, f"{args.output_dir}/medical_records", ['patientId', 'title', 'value'])
    
    print(f"\n✅ Complete! {len(patients)} patients, {len(all_records)} medical records")


if __name__ == '__main__':
    main()