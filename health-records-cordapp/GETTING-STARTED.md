# Getting Started - Health Records Corda CorDapp

## What is This?

A blockchain-based patient health records management system built on Corda. It allows hospitals to:
- Create patient profiles (ID, name, age)
- Add medical records (blood pressure, diagnoses, prescriptions, etc.)
- Query records by patient ID
- Store data immutably on a distributed ledger

## Prerequisites

- **Java 17** (required by Corda)
- **4GB RAM** minimum
- **Linux/Mac** (Windows with WSL2)

## Installation

### 1. Install Java 17 (if not installed)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk
```

**Mac:**
```bash
brew install openjdk@17
```

**Verify:**
```bash
java -version  # Should show version 17
```

### 2. Clone/Navigate to Project

```bash
cd health-records-cordapp
```

## Running the Application

### Option 1: Automated (Recommended)

```bash
./start-all.sh
```

Wait 45 seconds for everything to start.

### Option 2: Manual

**Terminal 1 - Start Nodes:**
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
cd build/nodes
./runnodes
```

**Terminal 2 - Start Web Server:**
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
./gradlew clients:runHospitalServer
```

### Option 3: Docker

```bash
docker-compose up
```

## Testing the API

### Quick Test

```bash
# Check if running
curl http://localhost:50005/api/me

# Should return: O=Hospital, L=London, C=GB
```

### Full Test

```bash
./test-api.sh
```

### Manual Testing

**1. Create a patient:**
```bash
curl -X POST http://localhost:50005/api/patients \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P001","name":"John Doe","age":35}'
```

**2. Add medical records:**
```bash
# Blood pressure
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Blood Pressure","value":"120/80 mmHg"}'

# Diagnosis
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Diagnosis","value":"Type 2 Diabetes"}'

# Prescription
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Prescription","value":"Metformin 500mg twice daily"}'
```

**3. Get all records for patient:**
```bash
curl http://localhost:50005/api/patients/P001/records
```

**4. Get all patients:**
```bash
curl http://localhost:50005/api/patients
```

## Understanding the Output

### Patient Response
```json
{
  "patientId": "P001",
  "name": "John Doe",
  "age": 35,
  "hospital": "O=Hospital, L=London, C=GB",
  "linearId": {
    "id": "abc123..."
  }
}
```

### Medical Record Response
```json
{
  "patientId": "P001",
  "title": "Blood Pressure",
  "value": "120/80 mmHg",
  "hospital": "O=Hospital, L=London, C=GB",
  "linearId": {
    "id": "def456..."
  }
}
```

## Common Issues

### "Unsupported Java version"

**Solution:** Set Java 17
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

### "Port already in use"

**Solution:** Kill existing processes
```bash
pkill -f corda.jar
pkill -f gradle
```

### "Schema validation error"

**Solution:** Run migrations
```bash
cd build/nodes/Hospital
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas
# Repeat for Doctor and Notary nodes
```

### Nodes won't start

**Solution:** Check logs
```bash
tail -f build/nodes/Hospital/logs/node-*.log
```

## Stopping the Application

```bash
# Stop all services
pkill -f corda.jar
pkill -f gradle
```

Or press `Ctrl+C` in each terminal.

## Next Steps

1. **Read the API Guide:** [API-GUIDE.md](API-GUIDE.md)
2. **Learn about deployment:** [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Understand the architecture:** [README.md](README.md)

## Architecture Overview

```
┌─────────────┐
│   Patient   │  (ID, Name, Age)
└─────────────┘
       │
       │ has many
       ▼
┌─────────────┐
│Medical      │  (Title, Value)
│Record       │
└─────────────┘
```

**Flow:**
1. Hospital creates patient → Stored on blockchain
2. Hospital adds medical records → Linked to patient ID
3. Records are immutable and timestamped by notary
4. Query records by patient ID

## File Structure

```
health-records-cordapp/
├── contracts/          # Smart contracts & states
├── workflows/          # Corda flows
├── clients/           # REST API
├── build/nodes/       # Deployed Corda nodes
├── start-all.sh       # One-command startup
├── test-api.sh        # API test script
├── API-GUIDE.md       # Complete API documentation
├── DEPLOYMENT.md      # Production deployment guide
└── README.md          # Technical documentation
```

## Support

**Issues?**
1. Check logs: `tail -f build/nodes/Hospital/logs/node-*.log`
2. Verify Java 17: `java -version`
3. Check ports: `netstat -tulpn | grep -E "1000[5-6]|50005"`

**Questions?**
- See [API-GUIDE.md](API-GUIDE.md) for API details
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Check Corda docs: https://docs.r3.com/

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./start-all.sh` | Start everything |
| `./test-api.sh` | Test the API |
| `curl http://localhost:50005/api/me` | Check if running |
| `pkill -f corda.jar` | Stop nodes |
| `tail -f build/nodes/Hospital/logs/node-*.log` | View logs |

## Example Use Cases

1. **Patient Registration**
   - Create patient with basic info
   - Store on blockchain

2. **Medical Records**
   - Add vital signs (BP, heart rate, temperature)
   - Add diagnoses
   - Add prescriptions
   - Add lab results

3. **Record Retrieval**
   - Get complete medical history by patient ID
   - View all patients in system

## Security Notes

- All data is stored on the blockchain (immutable)
- Only the hospital that created records can see them
- Transactions are signed and timestamped by notary
- RPC credentials should be changed for production

## Performance

- **Transaction time:** ~2-5 seconds
- **Query time:** <100ms
- **Throughput:** ~10-20 transactions/second
- **Storage:** ~1KB per record

## License

Apache License 2.0
