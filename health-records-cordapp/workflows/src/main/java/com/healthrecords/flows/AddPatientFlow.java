package com.healthrecords.flows;

import co.paralleluniverse.fibers.Suspendable;
import com.healthrecords.contracts.PatientContract;
import com.healthrecords.states.PatientState;
import net.corda.core.contracts.Command;
import net.corda.core.contracts.UniqueIdentifier;
import net.corda.core.flows.*;
import net.corda.core.identity.CordaX500Name;
import net.corda.core.identity.Party;
import net.corda.core.transactions.SignedTransaction;
import net.corda.core.transactions.TransactionBuilder;
import net.corda.core.utilities.ProgressTracker;
import net.corda.core.utilities.ProgressTracker.Step;

import java.util.Arrays;

public class AddPatientFlow {
    
    @InitiatingFlow
    @StartableByRPC
    public static class Initiator extends FlowLogic<SignedTransaction> {
        
        private final String patientId;
        private final String name;
        private final Integer age;
        
        public Initiator(String patientId, String name, Integer age) {
            this.patientId = patientId;
            this.name = name;
            this.age = age;
        }
        
        @Suspendable
        @Override
        public SignedTransaction call() throws FlowException {
            final Party notary = getServiceHub().getNetworkMapCache()
                    .getNotary(CordaX500Name.parse("O=Notary,L=London,C=GB"));
            
            Party hospital = getOurIdentity();
            PatientState patientState = new PatientState(
                    patientId,
                    name,
                    age,
                    hospital,
                    new UniqueIdentifier()
            );
            
            final Command<PatientContract.Commands.Create> txCommand = new Command<>(
                    new PatientContract.Commands.Create(),
                    Arrays.asList(patientState.getHospital().getOwningKey())
            );
            
            final TransactionBuilder txBuilder = new TransactionBuilder(notary)
                    .addOutputState(patientState, PatientContract.ID)
                    .addCommand(txCommand);
            
            txBuilder.verify(getServiceHub());
            
            final SignedTransaction signedTx = getServiceHub().signInitialTransaction(txBuilder);
            
            return subFlow(new FinalityFlow(signedTx, Arrays.asList()));
        }
    }
}
