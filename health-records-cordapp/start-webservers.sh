#!/bin/bash

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

echo "Starting Hospital web server on port 50005..."
./gradlew clients:runHospitalServer &

sleep 5

echo "Starting Doctor web server on port 50006..."
./gradlew clients:runDoctorServer &

echo ""
echo "Web servers starting..."
echo "Hospital API: http://localhost:50005/api"
echo "Doctor API: http://localhost:50006/api"
echo ""
echo "Press Ctrl+C to stop all servers"
wait
