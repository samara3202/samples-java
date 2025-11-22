#!/bin/bash

BASE_URL="http://localhost:50005/api"

echo "========================================="
echo "Health Records API Test"
echo "========================================="
echo ""

echo "Checking if API is available..."
if ! curl -s -f $BASE_URL/me > /dev/null 2>&1; then
    echo "❌ ERROR: API not available at $BASE_URL"
    echo "Make sure the web server is running:"
    echo "  ./gradlew clients:runHospitalServer"
    exit 1
fi
echo "✅ API is available"
echo ""

echo "1. Creating Patient P001..."
RESPONSE=$(curl -s -X POST $BASE_URL/patients \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P001","name":"John Doe","age":35}')
echo "$RESPONSE"
if [[ $RESPONSE == *"Error"* ]]; then
    echo "❌ Failed to create patient"
    exit 1
fi
echo "✅ Patient created"
echo ""

sleep 3

echo "2. Adding Blood Pressure record..."
RESPONSE=$(curl -s -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Blood Pressure","value":"120/80 mmHg"}')
echo "$RESPONSE"
if [[ $RESPONSE == *"Error"* ]]; then
    echo "❌ Failed to add record"
    exit 1
fi
echo "✅ Record added"
echo ""

sleep 2

echo "3. Adding Diagnosis record..."
curl -s -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Diagnosis","value":"Type 2 Diabetes"}'
echo ""
echo "✅ Record added"
echo ""

sleep 2

echo "4. Adding HbA1c Test result..."
curl -s -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"HbA1c Test","value":"7.2%"}'
echo ""
echo "✅ Record added"
echo ""

sleep 2

echo "5. Adding Prescription..."
curl -s -X POST $BASE_URL/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Prescription","value":"Metformin 500mg twice daily"}'
echo ""
echo "✅ Record added"
echo ""

sleep 3

echo "========================================="
echo "6. Retrieving all records for P001..."
echo "========================================="
curl -s $BASE_URL/patients/P001/records | python3 -m json.tool 2>/dev/null || curl -s $BASE_URL/patients/P001/records
echo -e "\n"

echo "========================================="
echo "7. Getting all patients..."
echo "========================================="
curl -s $BASE_URL/patients | python3 -m json.tool 2>/dev/null || curl -s $BASE_URL/patients
echo -e "\n"

echo "========================================="
echo "✅ Test Complete!"
echo "========================================="
