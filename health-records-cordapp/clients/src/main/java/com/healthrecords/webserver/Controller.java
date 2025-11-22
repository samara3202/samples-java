package com.healthrecords.webserver;

import com.healthrecords.flows.AddPatientFlow;
import com.healthrecords.flows.AddMedicalRecordFlow;
import com.healthrecords.flows.GetAllPatientsFlow;
import com.healthrecords.flows.GetPatientFlow;
import com.healthrecords.flows.GetPatientRecordsFlow;
import com.healthrecords.states.PatientState;
import com.healthrecords.states.MedicalRecordState;
import net.corda.core.messaging.CordaRPCOps;
import net.corda.core.transactions.SignedTransaction;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.concurrent.ExecutionException;

@RestController
@RequestMapping("/api")
public class Controller {
    
    private final CordaRPCOps proxy;
    
    public Controller(NodeRPCConnection rpc) {
        this.proxy = rpc.getProxy();
    }
    
    @PostMapping("/patients")
    public ResponseEntity<String> addPatient(@RequestBody PatientRequest request) {
        try {
            SignedTransaction result = proxy.startFlowDynamic(
                    AddPatientFlow.Initiator.class,
                    request.getPatientId(),
                    request.getName(),
                    request.getAge()
            ).getReturnValue().get();
            
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body("Patient created with transaction ID: " + result.getId());
            
        } catch (InterruptedException | ExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error creating patient: " + e.getMessage());
        }
    }
    
    @PostMapping("/patients/{patientId}/records")
    public ResponseEntity<String> addMedicalRecord(@PathVariable String patientId, 
                                                    @RequestBody MedicalRecordRequest request) {
        try {
            SignedTransaction result = proxy.startFlowDynamic(
                    AddMedicalRecordFlow.class,
                    patientId,
                    request.getTitle(),
                    request.getValue()
            ).getReturnValue().get();
            
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body("Medical record created with transaction ID: " + result.getId());
            
        } catch (InterruptedException | ExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error creating medical record: " + e.getMessage());
        }
    }
    
    @GetMapping("/patients/{patientId}/records")
    public ResponseEntity<List<MedicalRecordState>> getPatientRecords(@PathVariable String patientId) {
        try {
            List<MedicalRecordState> records = proxy.startFlowDynamic(
                    GetPatientRecordsFlow.class,
                    patientId
            ).getReturnValue().get();
            
            return ResponseEntity.ok(records);
            
        } catch (InterruptedException | ExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    @GetMapping("/patients")
    public ResponseEntity<List<PatientState>> getAllPatients() {
        try {
            List<PatientState> patients = proxy.startFlowDynamic(GetAllPatientsFlow.class)
                    .getReturnValue()
                    .get();
            
            return ResponseEntity.ok(patients);
            
        } catch (InterruptedException | ExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    @GetMapping("/patients/{patientId}")
    public ResponseEntity<List<PatientState>> getPatient(@PathVariable String patientId) {
        try {
            List<PatientState> patients = proxy.startFlowDynamic(
                    GetPatientFlow.class,
                    patientId
            ).getReturnValue().get();
            
            if (patients.isEmpty()) {
                return ResponseEntity.notFound().build();
            }
            
            return ResponseEntity.ok(patients);
            
        } catch (InterruptedException | ExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    @GetMapping("/me")
    public ResponseEntity<String> getNodeInfo() {
        return ResponseEntity.ok(proxy.nodeInfo().getLegalIdentities().get(0).getName().toString());
    }
    
    @GetMapping("/peers")
    public ResponseEntity<List<String>> getPeers() {
        List<String> peers = proxy.networkMapSnapshot().stream()
                .filter(nodeInfo -> !nodeInfo.getLegalIdentities().get(0).equals(proxy.nodeInfo().getLegalIdentities().get(0)))
                .map(nodeInfo -> nodeInfo.getLegalIdentities().get(0).getName().toString())
                .toList();
        
        return ResponseEntity.ok(peers);
    }
    
    public static class PatientRequest {
        private String patientId;
        private String name;
        private Integer age;
        
        public String getPatientId() {
            return patientId;
        }
        
        public void setPatientId(String patientId) {
            this.patientId = patientId;
        }
        
        public String getName() {
            return name;
        }
        
        public void setName(String name) {
            this.name = name;
        }
        
        public Integer getAge() {
            return age;
        }
        
        public void setAge(Integer age) {
            this.age = age;
        }
    }
    
    public static class MedicalRecordRequest {
        private String title;
        private String value;
        
        public String getTitle() {
            return title;
        }
        
        public void setTitle(String title) {
            this.title = title;
        }
        
        public String getValue() {
            return value;
        }
        
        public void setValue(String value) {
            this.value = value;
        }
    }
}
