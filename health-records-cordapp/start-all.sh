#!/bin/bash

set -e

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

echo "========================================="
echo "Health Records Corda - Complete Setup"
echo "========================================="
echo ""

# Check if we need to rebuild
REBUILD=false
if [ ! -d "build/nodes/Hospital" ]; then
    REBUILD=true
    echo "First time setup detected..."
elif [ -f "build/nodes/Hospital/persistence.mv.db" ]; then
    echo "Checking database schema..."
    # Check if old schema exists
    if grep -q "CLOB" build/nodes/Hospital/persistence.trace.db 2>/dev/null; then
        echo "Old schema detected, cleaning up..."
        rm -rf build/nodes/*/persistence* build/nodes/*/certificates build/nodes/*/network-parameters
        REBUILD=true
    fi
fi

if [ "$REBUILD" = true ]; then
    echo "Building and deploying nodes..."
    ./gradlew clean build deployNodes
    
    echo ""
    echo "Running database migrations..."
    cd build/nodes/Hospital && java -jar corda.jar run-migration-scripts --core-schemas --app-schemas > /dev/null 2>&1 && cd ../../..
    cd build/nodes/Doctor && java -jar corda.jar run-migration-scripts --core-schemas --app-schemas > /dev/null 2>&1 && cd ../../..
    cd build/nodes/Notary && java -jar corda.jar run-migration-scripts --core-schemas --app-schemas > /dev/null 2>&1 && cd ../../..
    echo "✅ Setup complete!"
else
    echo "✅ Nodes already deployed and up to date"
fi

echo ""
echo "========================================="
echo "Starting Corda Nodes..."
echo "========================================="
echo ""

# Start nodes in background
cd build/nodes
./runnodes &
NODES_PID=$!
cd ../..

# Wait for nodes to start
echo "Waiting for nodes to start (30 seconds)..."
sleep 30

echo ""
echo "========================================="
echo "Starting Hospital Web Server..."
echo "========================================="
echo ""

# Start web server
./gradlew clients:runHospitalServer &
WEB_PID=$!

echo ""
echo "Waiting for web server to start (15 seconds)..."
sleep 15

echo ""
echo "========================================="
echo "✅ All Services Started!"
echo "========================================="
echo ""
echo "Hospital API: http://localhost:50005/api"
echo ""
echo "Test the API:"
echo "  curl http://localhost:50005/api/me"
echo ""
echo "To stop all services:"
echo "  pkill -f corda.jar && pkill -f gradle"
echo ""
echo "Press Ctrl+C to view logs..."
echo "========================================="

# Keep script running
wait
