#!/bin/bash

set -e

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

echo "=== Health Records Corda CorDapp Setup ==="
echo ""

# Build
echo "Step 1/4: Building CorDapp..."
./gradlew clean build

# Deploy nodes
echo ""
echo "Step 2/4: Deploying nodes..."
./gradlew deployNodes

# Run migrations
echo ""
echo "Step 3/4: Running database migrations..."
cd build/nodes/Hospital
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas > /dev/null 2>&1
cd ../Doctor
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas > /dev/null 2>&1
cd ../Notary
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas > /dev/null 2>&1
cd ../../..

echo ""
echo "Step 4/4: Starting nodes..."
echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting Corda nodes..."
cd build/nodes
./runnodes
