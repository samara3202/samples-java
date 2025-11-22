#!/bin/bash

echo "Building CorDapp..."
./gradlew clean build deployNodes

echo ""
echo "Nodes deployed successfully!"
echo "To start the nodes, run: ./start-nodes.sh"
