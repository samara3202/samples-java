# Health Records API Guide

## Overview

The Health Records CorDapp provides a blockchain-based system for managing patient information and medical records.

**Data Model:**
- **Patient**: Basic patient information (ID, name, age)
- **Medical Record**: Health records linked to a patient (title, value)

## API Endpoints

Base URL: `http://localhost:50005/api` (Hospital node)

### 1. Create Patient

Create a new patient with basic information.

**Endpoint:** `POST /patients`

**Request Body:**
```json
{
  "patientId": "P001",
  "name": "John Doe",
  "age": 35
}
```

**Response:**
```
Patient created with transaction ID: <transaction-hash>
```

**Example:**
```bash
curl -X POST http://localhost:50005/api/patients \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P001","name":"John Doe","age":35}'
```

---

### 2. Add Medical Record

Add a medical record for an existing patient.

**Endpoint:** `POST /patients/{patientId}/records`

**Path Parameters:**
- `patientId`: The patient's ID

**Request Body:**
```json
{
  "title": "Blood Pressure",
  "value": "120/80 mmHg"
}
```

**Response:**
```
Medical record created with transaction ID: <transaction-hash>
```

**Examples:**
```bash
# Add blood pressure record
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Blood Pressure","value":"120/80 mmHg"}'

# Add diagnosis
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Diagnosis","value":"Type 2 Diabetes"}'

# Add prescription
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Prescription","value":"Metformin 500mg twice daily"}'

# Add lab result
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"HbA1c Test","value":"6.5%"}'
```

---

### 3. Get Patient Records

Retrieve all medical records for a specific patient.

**Endpoint:** `GET /patients/{patientId}/records`

**Path Parameters:**
- `patientId`: The patient's ID

**Response:**
```json
[
  {
    "patientId": "P001",
    "title": "Blood Pressure",
    "value": "120/80 mmHg",
    "hospital": "O=Hospital, L=London, C=GB",
    "linearId": {
      "externalId": null,
      "id": "abc123..."
    }
  },
  {
    "patientId": "P001",
    "title": "Diagnosis",
    "value": "Type 2 Diabetes",
    "hospital": "O=Hospital, L=London, C=GB",
    "linearId": {
      "externalId": null,
      "id": "def456..."
    }
  }
]
```

**Example:**
```bash
curl http://localhost:50005/api/patients/P001/records
```

---

### 4. Get All Patients

Retrieve all patients in the system.

**Endpoint:** `GET /patients`

**Response:**
```json
[
  {
    "patientId": "P001",
    "name": "John Doe",
    "age": 35,
    "hospital": "O=Hospital, L=London, C=GB",
    "linearId": {
      "externalId": null,
      "id": "xyz789..."
    }
  }
]
```

**Example:**
```bash
curl http://localhost:50005/api/patients
```

---

### 5. Get Patient by ID

Retrieve a specific patient by their patient ID.

**Endpoint:** `GET /patients/{patientId}`

**Path Parameters:**
- `patientId`: The patient's ID

**Response:**
```json
[
  {
    "patientId": "P001",
    "name": "John Doe",
    "age": 35,
    "hospital": "O=Hospital, L=London, C=GB",
    "linearId": {
      "externalId": null,
      "id": "xyz789..."
    }
  }
]
```

**Example:**
```bash
curl http://localhost:50005/api/patients/P001
```

---

### 6. Get Node Info

Get information about the current node.

**Endpoint:** `GET /me`

**Response:**
```
O=Hospital, L=London, C=GB
```

**Example:**
```bash
curl http://localhost:50005/api/me
```

---

### 7. Get Network Peers

Get list of other nodes in the network.

**Endpoint:** `GET /peers`

**Response:**
```json
[
  "O=Doctor, L=New York, C=US",
  "O=Notary, L=London, C=GB"
]
```

**Example:**
```bash
curl http://localhost:50005/api/peers
```

---

## Complete Workflow Example

### Step 1: Create a Patient

```bash
curl -X POST http://localhost:50005/api/patients \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P001","name":"John Doe","age":35}'
```

### Step 2: Add Multiple Medical Records

```bash
# Vital signs
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Blood Pressure","value":"120/80 mmHg"}'

curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Heart Rate","value":"72 bpm"}'

curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Temperature","value":"98.6°F"}'

# Diagnosis
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Diagnosis","value":"Type 2 Diabetes Mellitus"}'

# Lab results
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Fasting Blood Glucose","value":"126 mg/dL"}'

curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"HbA1c","value":"7.2%"}'

# Treatment
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Prescription","value":"Metformin 500mg - Take twice daily with meals"}'

curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Diet Plan","value":"Low carb diet, 1800 calories per day"}'
```

### Step 3: Retrieve All Records

```bash
curl http://localhost:50005/api/patients/P001/records | jq
```

---

## Error Responses

### 400 Bad Request
Invalid request data or missing required fields.

### 404 Not Found
Patient or record not found.

### 500 Internal Server Error
Server error or flow execution failure.

---

## Notes

- All data is stored on the Corda blockchain
- Records are immutable once created
- Only the hospital that created the record can see it
- Patient IDs must be unique
- All timestamps are managed by the Corda notary

---

## Testing Script

Save this as `test-api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:50005/api"

echo "=== Creating Patient ==="
curl -X POST $BASE_URL/patients \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P001","name":"John Doe","age":35}'
echo -e "\n"

sleep 2

echo "=== Adding Medical Records ==="
curl -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Blood Pressure","value":"120/80 mmHg"}'
echo -e "\n"

curl -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Diagnosis","value":"Type 2 Diabetes"}'
echo -e "\n"

sleep 2

echo "=== Retrieving Patient Records ==="
curl $BASE_URL/patients/P001/records | jq
echo -e "\n"

echo "=== Getting All Patients ==="
curl $BASE_URL/patients | jq
```

Run with: `chmod +x test-api.sh && ./test-api.sh`
