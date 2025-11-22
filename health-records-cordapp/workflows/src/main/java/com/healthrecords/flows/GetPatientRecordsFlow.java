package com.healthrecords.flows;

import co.paralleluniverse.fibers.Suspendable;
import com.healthrecords.states.MedicalRecordState;
import net.corda.core.contracts.StateAndRef;
import net.corda.core.flows.FlowException;
import net.corda.core.flows.FlowLogic;
import net.corda.core.flows.InitiatingFlow;
import net.corda.core.flows.StartableByRPC;
import net.corda.core.node.services.Vault;
import net.corda.core.node.services.vault.QueryCriteria;

import java.util.List;
import java.util.stream.Collectors;

@InitiatingFlow
@StartableByRPC
public class GetPatientRecordsFlow extends FlowLogic<List<MedicalRecordState>> {
    
    private final String patientId;
    
    public GetPatientRecordsFlow(String patientId) {
        this.patientId = patientId;
    }
    
    @Suspendable
    @Override
    public List<MedicalRecordState> call() throws FlowException {
        QueryCriteria queryCriteria = new QueryCriteria.VaultQueryCriteria(Vault.StateStatus.UNCONSUMED);
        
        List<StateAndRef<MedicalRecordState>> medicalRecords = getServiceHub().getVaultService()
                .queryBy(MedicalRecordState.class, queryCriteria)
                .getStates();
        
        return medicalRecords.stream()
                .map(StateAndRef::getState)
                .map(state -> state.getData())
                .filter(record -> record.getPatientId().equals(patientId))
                .collect(Collectors.toList());
    }
}
