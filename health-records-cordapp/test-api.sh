#!/bin/bash

BASE_URL="http://localhost:50005/api"

echo "========================================="
echo "Health Records API Test"
echo "========================================="
echo ""

echo "1. Creating Patient P001..."
curl -X POST $BASE_URL/patients \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P001","name":"John Doe","age":35}'
echo -e "\n"

sleep 2

echo "2. Adding Blood Pressure record..."
curl -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Blood Pressure","value":"120/80 mmHg"}'
echo -e "\n"

sleep 1

echo "3. Adding Diagnosis record..."
curl -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Diagnosis","value":"Type 2 Diabetes"}'
echo -e "\n"

sleep 1

echo "4. Adding HbA1c Test result..."
curl -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"HbA1c Test","value":"7.2%"}'
echo -e "\n"

sleep 1

echo "5. Adding Prescription..."
curl -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Prescription","value":"Metformin 500mg twice daily"}'
echo -e "\n"

sleep 2

echo "========================================="
echo "6. Retrieving all records for P001..."
echo "========================================="
curl $BASE_URL/patients/P001/records
echo -e "\n\n"

echo "========================================="
echo "7. Getting all patients..."
echo "========================================="
curl $BASE_URL/patients
echo -e "\n\n"

echo "========================================="
echo "Test Complete!"
echo "========================================="
