FROM eclipse-temurin:17-jdk

# Install required tools
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . .

# Make gradlew executable
RUN chmod +x gradlew

# Build the project
RUN ./gradlew clean build -x test

# Deploy nodes
RUN ./gradlew deployNodes

# Run migrations for all nodes
RUN cd build/nodes/Hospital && java -jar corda.jar run-migration-scripts --core-schemas --app-schemas && cd ../../..
RUN cd build/nodes/Doctor && java -jar corda.jar run-migration-scripts --core-schemas --app-schemas && cd ../../..
RUN cd build/nodes/Notary && java -jar corda.jar run-migration-scripts --core-schemas --app-schemas && cd ../../..

# Expose ports
# Notary: 10002 (p2p), 10003 (rpc)
# Hospital: 10005 (p2p), 10006 (rpc), 50005 (web)
# Doctor: 10008 (p2p), 10009 (rpc), 50006 (web)
EXPOSE 10002 10003 10005 10006 10008 10009 50005 50006

# Default command - start nodes
CMD ["bash", "-c", "cd build/nodes && ./runnodes"]
