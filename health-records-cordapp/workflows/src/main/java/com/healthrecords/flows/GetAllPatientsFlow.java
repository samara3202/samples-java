package com.healthrecords.flows;

import co.paralleluniverse.fibers.Suspendable;
import com.healthrecords.states.PatientState;
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
public class GetAllPatientsFlow extends FlowLogic<List<PatientState>> {
    
    @Suspendable
    @Override
    public List<PatientState> call() throws FlowException {
        QueryCriteria queryCriteria = new QueryCriteria.VaultQueryCriteria(Vault.StateStatus.UNCONSUMED);
        
        List<StateAndRef<PatientState>> patientStates = getServiceHub().getVaultService()
                .queryBy(PatientState.class, queryCriteria)
                .getStates();
        
        return patientStates.stream()
                .map(StateAndRef::getState)
                .map(state -> state.getData())
                .collect(Collectors.toList());
    }
}
