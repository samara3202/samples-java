#!/bin/bash

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

echo "========================================="
echo "Restarting Services"
echo "========================================="
echo ""

echo "Stopping old processes..."
pkill -f corda.jar 2>/dev/null || true
pkill -f gradle 2>/dev/null || true
sleep 3

echo "Rebuilding..."
./gradlew build -x test
./gradlew deployNodes

echo ""
echo "========================================="
echo "✅ Rebuild Complete!"
echo "========================================="
echo ""
echo "Now run in separate terminals:"
echo ""
echo "Terminal 1:"
echo "  cd build/nodes && ./runnodes"
echo ""
echo "Terminal 2:"
echo "  ./gradlew clients:runHospitalServer"
echo ""
