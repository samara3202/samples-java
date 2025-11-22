# Health Records Corda CorDapp

A Corda blockchain application for managing patient health records with distributed ledger technology. This CorDapp enables hospitals and doctors to securely create and share patient records across a Corda network.

## Overview

This application demonstrates:
- **Distributed Ledger**: Patient records stored on Corda blockchain
- **Multi-Party Transactions**: Hospital and doctor must both sign patient records
- **Privacy**: Only participants (hospital and doctor) can see the records
- **Immutability**: Records are tamper-proof once committed to the ledger
- **Query Capabilities**: Retrieve patient records by patient ID

## Architecture

### Components

1. **States** (`contracts` module)
   - `PatientState`: Represents a patient health record with patientId, name, age, hospital, and doctor

2. **Contracts** (`contracts` module)
   - `PatientContract`: Validates patient record creation rules

3. **Flows** (`workflows` module)
   - `AddPatientFlow`: Creates a new patient record (requires hospital and doctor signatures)
   - `GetPatientFlow`: Retrieves patient records by patient ID
   - `GetAllPatientsFlow`: Retrieves all patient records

4. **Client API** (`clients` module)
   - REST API for interacting with Corda nodes
   - Spring Boot application

### Network Nodes

- **Notary** (London): Validates and timestamps transactions
- **Hospital** (London): Creates patient records
- **Doctor** (New York): Co-signs patient records

## Prerequisites

- Java 17 (Corda requires Java 17)
- Gradle 8.5+
- Docker (optional, for containerization)

## Quick Start

### One-Command Start (Easiest)

```bash
cd health-records-cordapp
./start-all.sh
```

This automatically:
- Builds the project
- Deploys nodes
- Runs migrations
- Starts all services

**API Available at:** http://localhost:50005/api

### Manual Build

```bash
cd health-records-cordapp
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
./gradlew clean build
```

### 2. Deploy Corda Nodes

```bash
./gradlew deployNodes
```

This creates three nodes in `build/nodes/`:
- Notary
- Hospital
- Doctor

### 3. Run Database Migration (First Time Only)

```bash
# Migrate Hospital node
cd build/nodes/Hospital
/usr/lib/jvm/java-17-openjdk-amd64/bin/java -jar corda.jar run-migration-scripts --core-schemas --app-schemas

# Migrate Doctor node
cd ../Doctor
/usr/lib/jvm/java-17-openjdk-amd64/bin/java -jar corda.jar run-migration-scripts --core-schemas --app-schemas

# Migrate Notary node
cd ../Notary
/usr/lib/jvm/java-17-openjdk-amd64/bin/java -jar corda.jar run-migration-scripts --core-schemas --app-schemas

cd ../../..
```

### 4. Start the Nodes

**Option 1: Using the helper script**
```bash
./start-nodes-java17.sh
```

**Option 2: Manual start**
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
cd build/nodes
./runnodes
```

Wait for all nodes to start (you'll see "Node started up and registered" messages).

### 5. Start the Web Servers

In a new terminal:

**Option 1: Using the helper script (starts both servers)**
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
./start-webservers.sh
```

**Option 2: Manual start (separate terminals)**
```bash
# Terminal 1: Start Hospital web server (port 50005)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
./gradlew clients:runHospitalServer

# Terminal 2: Start Doctor web server (port 50006)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
./gradlew clients:runDoctorServer
```

## API Usage

See [API-GUIDE.md](API-GUIDE.md) for complete API documentation.

### Quick Examples

#### 1. Create a Patient

```bash
curl -X POST http://localhost:50005/api/patients \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P001","name":"John Doe","age":35}'
```

#### 2. Add Medical Record

```bash
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Blood Pressure","value":"120/80 mmHg"}'
```

#### 3. Get Patient Records

```bash
curl http://localhost:50005/api/patients/P001/records
```

#### 4. Get All Patients

```bash
curl http://localhost:50005/api/patients
```

## How It Works

### Data Model

**Patient**: Stores basic patient information
- Patient ID (unique identifier)
- Name
- Age
- Hospital (creator)

**Medical Record**: Stores health records linked to a patient
- Patient ID (reference to patient)
- Title (e.g., "Blood Pressure", "Diagnosis")
- Value (the actual medical data)
- Hospital (creator)

### Adding a Patient

1. **Hospital initiates** the flow with patient details (ID, name, age)
2. **Transaction is built** with PatientState as output
3. **Hospital signs** the transaction
4. **Notary validates** and timestamps the transaction
5. **Transaction is finalized** and recorded in Hospital's vault

### Adding a Medical Record

1. **Hospital initiates** the flow with patient ID, title, and value
2. **Transaction is built** with MedicalRecordState as output
3. **Hospital signs** the transaction
4. **Notary validates** and timestamps the transaction
5. **Transaction is finalized** and recorded in Hospital's vault

### Querying Records

- Each node maintains its own vault with records it created
- Queries are performed locally against the node's vault
- Medical records are linked to patients via patient ID
- Only the hospital that created the records can see them

## Project Structure

```
health-records-cordapp/
├── contracts/
│   └── src/main/java/com/healthrecords/
│       ├── states/
│       │   └── PatientState.java
│       ├── contracts/
│       │   └── PatientContract.java
│       └── schema/
│           ├── PatientSchema.java
│           └── PatientSchemaV1.java
├── workflows/
│   └── src/main/java/com/healthrecords/flows/
│       ├── AddPatientFlow.java
│       ├── GetPatientFlow.java
│       └── GetAllPatientsFlow.java
├── clients/
│   └── src/main/java/com/healthrecords/webserver/
│       ├── Starter.java
│       ├── Controller.java
│       └── NodeRPCConnection.java
├── build.gradle
├── settings.gradle
└── README.md
```

## Testing with Corda Shell

You can also interact with nodes directly using the Corda shell:

### Connect to Hospital Node

```bash
cd build/nodes/Hospital
java -jar corda-shell-4.12.jar --host=localhost --port=10006 --user=user1 --password=test
```

### Run Flows from Shell

```corda
# Add a patient record
flow start AddPatientFlow$Initiator patientId: "P002", name: "Jane Smith", age: 28, doctor: "O=Doctor, L=New York, C=US"

# Get all patients
flow start GetAllPatientsFlow

# Get patient by ID
flow start GetPatientFlow patientId: "P002"
```

## Key Features

### 1. Multi-Party Consensus
- Both hospital and doctor must sign patient records
- Ensures data integrity and agreement

### 2. Privacy
- Only transaction participants can see the data
- Other nodes on the network cannot access the records

### 3. Immutability
- Once recorded, patient records cannot be altered
- Complete audit trail of all transactions

### 4. Distributed
- No central authority
- Each node maintains its own copy of relevant data

### 5. Queryable
- Fast local queries against node's vault
- Filter by patient ID or retrieve all records

## Contract Rules

The `PatientContract` enforces:
- No input states when creating a patient record
- Exactly one output state
- Patient ID must not be empty
- Patient name must not be empty
- Patient age must be positive
- Hospital and doctor must be different entities
- All participants must sign the transaction

## Troubleshooting

### Java Version Issues

Corda requires Java 17. Set it explicitly:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

### Port Conflicts

If ports are in use, modify `build.gradle` deployNodes section:
- Notary: p2pPort 10002, rpcPort 10003
- Hospital: p2pPort 10005, rpcPort 10006
- Doctor: p2pPort 10008, rpcPort 10009

### Node Startup Issues

Check logs in `build/nodes/<NodeName>/logs/`

### Web Server Connection Issues

Ensure:
1. Nodes are running
2. RPC ports are accessible
3. Credentials match (user1/test)

## Docker Deployment (Optional)

### Build Docker Images

```bash
# Build node images
docker build -t health-records-node:latest .

# Build client image
docker build -t health-records-client:latest -f clients/Dockerfile .
```

### Run with Docker Compose

```bash
docker-compose up
```

## Security Considerations

- **Production Use**: Change default RPC credentials
- **TLS**: Enable TLS for RPC connections
- **Network**: Use proper network configuration
- **Access Control**: Implement proper authentication/authorization
- **Key Management**: Secure node keys properly

## Future Enhancements

- Add patient record updates (with version control)
- Implement record sharing with other healthcare providers
- Add medical history and diagnosis fields
- Implement access control lists
- Add encryption for sensitive data
- Integrate with existing healthcare systems

## License

Apache License 2.0

## Support

For Corda documentation: [https://docs.r3.com/](https://docs.r3.com/)

For issues: Create an issue in the repository
