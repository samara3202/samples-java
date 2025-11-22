#!/bin/bash
set -e

echo "========================================="
echo "Clean Rebuild & Setup"
echo "========================================="

# 1. Stop everything
echo "Stopping processes..."
pkill -f corda.jar 2>/dev/null || true
pkill -f gradle 2>/dev/null || true
sleep 3

# 2. Navigate to project root (works from any location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT"

# 3. Set Java 17
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 4. Clean old database and build artifacts
echo "Cleaning old data..."
rm -rf build/nodes/*/persistence*
rm -rf build/nodes/*/certificates
rm -rf build/nodes/*/network-parameters
rm -rf build/nodes/*/logs

# 5. Build project
echo "Building project..."
./gradlew clean build -x test

# 6. Deploy nodes
echo "Deploying nodes..."
./gradlew deployNodes

# 7. Run migrations for all nodes
echo "Running database migrations..."
cd build/nodes/Hospital && java -jar corda.jar run-migration-scripts --core-schemas --app-schemas && cd ../../..
cd build/nodes/Doctor && java -jar corda.jar run-migration-scripts --core-schemas --app-schemas && cd ../../..
cd build/nodes/Notary && java -jar corda.jar run-migration-scripts --core-schemas --app-schemas && cd ../../..

echo "========================================="
echo "✅ Clean Setup Complete!"
echo "========================================="
echo ""
echo "To start the application:"
echo "  Terminal 1: cd build/nodes && ./runnodes"
echo "  Terminal 2: ./gradlew clients:runHospitalServer"
echo ""