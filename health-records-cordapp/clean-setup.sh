#!/bin/bash

set -e

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

echo "========================================="
echo "Clean Setup - Health Records Corda"
echo "========================================="
echo ""

echo "Step 1: Stopping any running nodes..."
pkill -f corda.jar 2>/dev/null || true
pkill -f gradle 2>/dev/null || true
sleep 2

echo "Step 2: Cleaning old data..."
rm -rf build/nodes/*/persistence*
rm -rf build/nodes/*/certificates
rm -rf build/nodes/*/network-parameters
echo "✅ Cleaned"

echo ""
echo "Step 3: Building project..."
./gradlew clean build -x test

echo ""
echo "Step 4: Deploying nodes..."
./gradlew deployNodes

echo ""
echo "Step 5: Running database migrations..."
cd build/nodes/Hospital
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas
cd ../Doctor
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas
cd ../Notary
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas
cd ../../..

echo ""
echo "========================================="
echo "✅ Clean Setup Complete!"
echo "========================================="
echo ""
echo "Now run: ./start-all.sh"
echo "Or manually:"
echo "  Terminal 1: cd build/nodes && ./runnodes"
echo "  Terminal 2: ./gradlew clients:runHospitalServer"
echo ""
