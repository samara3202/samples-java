# 🏥 Health Records Corda CorDapp - START HERE

## ⚡ Quick Start (3 Steps)

### 1️⃣ Navigate to Project
```bash
cd /workspaces/samples-java/health-records-cordapp
```

### 2️⃣ Start Everything
```bash
./start-all.sh
```

### 3️⃣ Test the API
```bash
./test-api.sh
```

**Done!** Your blockchain health records system is running at http://localhost:50005/api

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[GETTING-STARTED.md](GETTING-STARTED.md)** | Complete beginner guide |
| **[API-GUIDE.md](API-GUIDE.md)** | All API endpoints with examples |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Production deployment (Docker, Cloud, K8s) |
| **[README.md](README.md)** | Technical architecture details |

---

## 🎯 What Can You Do?

### Create Patients
```bash
curl -X POST http://localhost:50005/api/patients \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P001","name":"John Doe","age":35}'
```

### Add Medical Records
```bash
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Blood Pressure","value":"120/80 mmHg"}'
```

### Get Patient Records
```bash
curl http://localhost:50005/api/patients/P001/records
```

---

## 🏗️ Architecture

```
Patient (ID, Name, Age)
    │
    └─► Medical Records (Title, Value)
            │
            └─► Stored on Corda Blockchain
```

**3 Nodes:**
- **Notary** (London) - Validates transactions
- **Hospital** (London) - Creates records
- **Doctor** (New York) - Can view records

---

## 🐛 Troubleshooting

### Schema validation errors?
```bash
# Run clean setup (fixes all schema issues)
./clean-setup.sh
```

### Nodes won't start?
```bash
# Check Java version (must be 17)
java -version

# Set Java 17
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

### Port conflicts?
```bash
# Stop everything
pkill -f corda.jar
pkill -f gradle
```

### Complete reset?
```bash
# Clean everything and rebuild
./clean-setup.sh
```

---

## 🚀 Deployment Options

### Local (Development)
```bash
./start-all.sh
```

### Docker
```bash
docker-compose up
```

### Production
See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- AWS/Azure/GCP deployment
- Kubernetes setup
- Security hardening
- Monitoring & scaling

---

## 📊 Example Workflow

```bash
# 1. Create patient
curl -X POST http://localhost:50005/api/patients \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P001","name":"John Doe","age":35}'

# 2. Add vital signs
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Blood Pressure","value":"120/80 mmHg"}'

curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Heart Rate","value":"72 bpm"}'

# 3. Add diagnosis
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Diagnosis","value":"Type 2 Diabetes"}'

# 4. Add prescription
curl -X POST http://localhost:50005/api/patients/P001/records \
  -H "Content-Type: application/json" \
  -d '{"title":"Prescription","value":"Metformin 500mg twice daily"}'

# 5. Get all records
curl http://localhost:50005/api/patients/P001/records
```

---

## ✅ Features

- ✅ Blockchain-based (immutable records)
- ✅ Patient management (ID, name, age)
- ✅ Medical records (unlimited per patient)
- ✅ REST API (easy integration)
- ✅ Docker support (easy deployment)
- ✅ Production-ready (see DEPLOYMENT.md)

---

## 🔧 Tech Stack

- **Blockchain:** Corda 4.12
- **Language:** Java 17
- **Build:** Gradle 8.5
- **API:** Spring Boot 3.2
- **Database:** H2 (dev), PostgreSQL (prod)

---

## 📝 Quick Commands

```bash
# Start everything
./start-all.sh

# Test API
./test-api.sh

# Stop everything
pkill -f corda.jar && pkill -f gradle

# View logs
tail -f build/nodes/Hospital/logs/node-*.log

# Check if running
curl http://localhost:50005/api/me

# Rebuild
./gradlew clean build deployNodes
```

---

## 🎓 Learning Path

1. **Start:** Run `./start-all.sh`
2. **Test:** Run `./test-api.sh`
3. **Explore:** Read [API-GUIDE.md](API-GUIDE.md)
4. **Understand:** Read [README.md](README.md)
5. **Deploy:** Read [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 💡 Tips

- **First time?** Use `./start-all.sh` - it handles everything
- **Testing?** Use `./test-api.sh` - creates sample data
- **Deploying?** See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- **Issues?** Check logs in `build/nodes/*/logs/`

---

## 🌐 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/patients` | Create patient |
| GET | `/api/patients` | Get all patients |
| GET | `/api/patients/{id}` | Get patient by ID |
| POST | `/api/patients/{id}/records` | Add medical record |
| GET | `/api/patients/{id}/records` | Get patient records |
| GET | `/api/me` | Get node info |
| GET | `/api/peers` | Get network peers |

---

## 🎉 You're Ready!

Run this now:
```bash
cd /workspaces/samples-java/health-records-cordapp
./start-all.sh
```

Then test:
```bash
./test-api.sh
```

**Questions?** Check the documentation files listed at the top!
