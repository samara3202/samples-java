# Quick Start Guide

## Prerequisites

Ensure Java 17 is installed:
```bash
java -version  # Should show version 17
```

If not, install it:
```bash
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk
```

## Automated Setup (Recommended)

### One-Command Setup and Start

```bash
cd health-records-cordapp
./setup-and-start.sh
```

This script will:
1. Build the CorDapp
2. Deploy the nodes
3. Run database migrations
4. Start all nodes

Wait until you see "Node started up and registered" for all 3 nodes.

## Manual Setup (Alternative)

### 1. Build the CorDapp

```bash
cd health-records-cordapp
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
./gradlew clean build
```

### 2. Deploy Nodes

```bash
./gradlew deployNodes
```

This creates the network in `build/nodes/` with:
- Notary (London)
- Hospital (London) 
- Doctor (New York)

### 3. Run Database Migrations (REQUIRED - First Time)

```bash
cd build/nodes/Hospital
/usr/lib/jvm/java-17-openjdk-amd64/bin/java -jar corda.jar run-migration-scripts --core-schemas --app-schemas

cd ../Doctor
/usr/lib/jvm/java-17-openjdk-amd64/bin/java -jar corda.jar run-migration-scripts --core-schemas --app-schemas

cd ../Notary
/usr/lib/jvm/java-17-openjdk-amd64/bin/java -jar corda.jar run-migration-scripts --core-schemas --app-schemas

cd ../../..
```

⚠️ **Important**: You must see "Running Changeset: migration/patient.changelog-master.xml" for each node.

### 4. Start Corda Nodes

**Terminal 1:**
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
cd build/nodes
./runnodes
```

Wait until you see messages like:
```
Node started up and registered in X.XX sec
```

### 5. Start Web Servers

**Terminal 2:**
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
./gradlew clients:runHospitalServer
```

**Terminal 3:**
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
./gradlew clients:runDoctorServer
```

Wait for Spring Boot to start (you'll see "Started Starter in X seconds").

### 6. Test the API

**Terminal 4:**

Check Hospital node identity:
```bash
curl http://localhost:50005/api/me
```

Add a patient record:
```bash
curl -X POST http://localhost:50005/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "patientId": "P001",
    "name": "John Doe",
    "age": 35,
    "doctorName": "O=Doctor, L=New York, C=US"
  }'
```

Get all patients:
```bash
curl http://localhost:50005/api/patients
```

Get specific patient:
```bash
curl http://localhost:50005/api/patients/P001
```

Check from Doctor's perspective:
```bash
curl http://localhost:50006/api/patients
```

## Common Issues

### Issue: "Unsupported Java version"
**Solution:** Always set JAVA_HOME before running commands:
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

### Issue: "missing table [patient_states]"
**Solution:** Run the database migration scripts (Step 3 above)

### Issue: Port already in use
**Solution:** Kill existing processes:
```bash
pkill -f corda.jar
pkill -f gradle
```

### Issue: Nodes won't start
**Solution:** Check logs:
```bash
tail -f build/nodes/Hospital/logs/node-*.log
```

## What's Happening?

1. **Hospital** creates a patient record
2. Transaction is sent to **Doctor** for signature
3. Both parties sign the transaction
4. **Notary** validates and timestamps it
5. Transaction is finalized and stored in both Hospital and Doctor vaults
6. Both parties can now query the patient record

## Next Steps

- Try adding more patient records
- Query from both Hospital and Doctor nodes
- Check the Corda shell (see main README)
- Explore the code in `contracts/`, `workflows/`, and `clients/`

## Stopping Everything

```bash
# Stop nodes
pkill -f corda.jar

# Stop web servers
pkill -f gradle
```

Or just press `Ctrl+C` in each terminal.
