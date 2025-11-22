# Deployment Guide

## Quick Start (Easiest)

### Option 1: One-Command Start

```bash
cd health-records-cordapp
./start-all.sh
```

This will:
1. Build the project (if needed)
2. Deploy Corda nodes
3. Run database migrations
4. Start all nodes
5. Start the web server

**Access the API:** http://localhost:50005/api

---

## Manual Deployment

### Prerequisites

- Java 17
- Gradle 8.5+
- 4GB RAM minimum

### Step 1: Build

```bash
cd health-records-cordapp
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
./gradlew clean build
```

### Step 2: Deploy Nodes

```bash
./gradlew deployNodes
```

### Step 3: Run Migrations

```bash
cd build/nodes/Hospital
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas

cd ../Doctor
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas

cd ../Notary
java -jar corda.jar run-migration-scripts --core-schemas --app-schemas

cd ../../..
```

### Step 4: Start Nodes

**Terminal 1:**
```bash
cd build/nodes
./runnodes
```

Wait for "Node started up and registered" messages (about 30 seconds).

### Step 5: Start Web Server

**Terminal 2:**
```bash
./gradlew clients:runHospitalServer
```

Wait for "Started Starter" message.

### Step 6: Test

**Terminal 3:**
```bash
./test-api.sh
```

Or manually:
```bash
curl http://localhost:50005/api/me
```

---

## Docker Deployment

### Build Docker Image

```bash
docker build -t health-records-corda:latest .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

This starts:
- Notary node (ports 10002, 10003)
- Hospital node (ports 10005, 10006)
- Doctor node (ports 10008, 10009)
- Hospital web server (port 50005)

**Access the API:** http://localhost:50005/api

### Check Status

```bash
docker-compose ps
docker-compose logs -f hospital
```

### Stop Services

```bash
docker-compose down
```

---

## Production Deployment

### System Requirements

- **CPU:** 4 cores minimum
- **RAM:** 8GB minimum (2GB per node + 2GB for web server)
- **Disk:** 20GB minimum
- **OS:** Linux (Ubuntu 20.04+ recommended)

### Security Considerations

1. **Change Default Credentials**
   - Edit `build/nodes/*/node.conf`
   - Update RPC username/password

2. **Enable TLS**
   - Configure SSL certificates
   - Update `application.properties`

3. **Firewall Rules**
   - Allow only necessary ports
   - Restrict RPC access to localhost

4. **Database**
   - Use PostgreSQL instead of H2
   - Configure backups

### Environment Variables

```bash
export JAVA_OPTS="-Xmx2g -Xms1g"
export CORDA_HOME=/opt/corda
```

### Systemd Service (Linux)

Create `/etc/systemd/system/corda-hospital.service`:

```ini
[Unit]
Description=Corda Hospital Node
After=network.target

[Service]
Type=simple
User=corda
WorkingDirectory=/opt/corda/health-records-cordapp/build/nodes/Hospital
ExecStart=/usr/bin/java -jar corda.jar
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable corda-hospital
sudo systemctl start corda-hospital
sudo systemctl status corda-hospital
```

---

## Cloud Deployment

### AWS

1. **EC2 Instance**
   - Type: t3.medium or larger
   - AMI: Ubuntu 20.04 LTS
   - Security Group: Open ports 10002-10009, 50005

2. **Setup Script**
```bash
#!/bin/bash
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk git
git clone <your-repo>
cd health-records-cordapp
./start-all.sh
```

### Azure

1. **Virtual Machine**
   - Size: Standard_B2s or larger
   - Image: Ubuntu 20.04 LTS
   - Network: Open required ports

2. **Deploy**
```bash
az vm create \
  --resource-group health-records-rg \
  --name corda-node \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys
```

### Google Cloud

1. **Compute Engine**
   - Machine type: e2-medium or larger
   - Boot disk: Ubuntu 20.04 LTS
   - Firewall: Allow required ports

2. **Deploy**
```bash
gcloud compute instances create corda-node \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB
```

---

## Kubernetes Deployment

### Create Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: corda-hospital
spec:
  replicas: 1
  selector:
    matchLabels:
      app: corda-hospital
  template:
    metadata:
      labels:
        app: corda-hospital
    spec:
      containers:
      - name: corda
        image: health-records-corda:latest
        ports:
        - containerPort: 10005
        - containerPort: 10006
        - containerPort: 50005
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

### Create Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: hospital-api
spec:
  type: LoadBalancer
  ports:
  - port: 50005
    targetPort: 50005
  selector:
    app: corda-hospital
```

Apply:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## Monitoring

### Health Checks

```bash
# Check node status
curl http://localhost:10006/health

# Check web server
curl http://localhost:50005/api/me

# Check peers
curl http://localhost:50005/api/peers
```

### Logs

```bash
# Node logs
tail -f build/nodes/Hospital/logs/node-*.log

# Web server logs
tail -f build/nodes/Hospital/logs/web-*.log
```

### Metrics

Jolokia endpoints available at:
- Hospital: http://localhost:7007/jolokia/
- Doctor: http://localhost:7006/jolokia/
- Notary: http://localhost:7005/jolokia/

---

## Troubleshooting

### Nodes Won't Start

1. Check Java version: `java -version` (must be 17)
2. Check logs: `tail -f build/nodes/*/logs/node-*.log`
3. Verify migrations: Run migration scripts again
4. Check ports: `netstat -tulpn | grep -E "1000[2-9]"`

### Schema Errors

```bash
# Drop and recreate database
rm -rf build/nodes/*/persistence*
./gradlew deployNodes
# Run migrations again
```

### Port Conflicts

Edit `build.gradle` and change port numbers in `deployNodes` task.

### Out of Memory

Increase heap size:
```bash
export JAVA_OPTS="-Xmx4g -Xms2g"
```

---

## Backup and Recovery

### Backup

```bash
# Backup node data
tar -czf backup-$(date +%Y%m%d).tar.gz build/nodes/*/persistence*

# Backup configuration
tar -czf config-backup.tar.gz build/nodes/*/node.conf
```

### Restore

```bash
# Stop nodes
pkill -f corda.jar

# Restore data
tar -xzf backup-20231122.tar.gz

# Restart nodes
cd build/nodes && ./runnodes
```

---

## Scaling

### Horizontal Scaling

Add more hospital nodes by modifying `build.gradle`:

```groovy
node {
    name "O=Hospital2,L=Manchester,C=GB"
    p2pPort 10011
    rpcSettings {
        address("localhost:10012")
        adminAddress("localhost:10052")
    }
    rpcUsers = [[ user: "user1", "password": "test", "permissions": ["ALL"]]]
}
```

### Load Balancing

Use nginx or HAProxy to distribute API requests:

```nginx
upstream hospital_api {
    server localhost:50005;
    server localhost:50007;
}

server {
    listen 80;
    location /api {
        proxy_pass http://hospital_api;
    }
}
```

---

## Support

For issues:
1. Check logs in `build/nodes/*/logs/`
2. Review [API-GUIDE.md](API-GUIDE.md)
3. See [README.md](README.md) for architecture details
