package com.healthrecords.flows;

import co.paralleluniverse.fibers.Suspendable;
import com.healthrecords.contracts.MedicalRecordContract;
import com.healthrecords.states.MedicalRecordState;
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

@InitiatingFlow
@StartableByRPC
public class AddMedicalRecordFlow extends FlowLogic<SignedTransaction> {
    
    private final String patientId;
    private final String title;
    private final String value;
    
    public AddMedicalRecordFlow(String patientId, String title, String value) {
        this.patientId = patientId;
        this.title = title;
        this.value = value;
    }
    
    @Suspendable
    @Override
    public SignedTransaction call() throws FlowException {
        final Party notary = getServiceHub().getNetworkMapCache()
                .getNotary(CordaX500Name.parse("O=Notary,L=London,C=GB"));
        
        Party hospital = getOurIdentity();
        MedicalRecordState medicalRecordState = new MedicalRecordState(
                patientId,
                title,
                value,
                hospital,
                new UniqueIdentifier()
        );
        
        final Command<MedicalRecordContract.Commands.Create> txCommand = new Command<>(
                new MedicalRecordContract.Commands.Create(),
                Arrays.asList(medicalRecordState.getHospital().getOwningKey())
        );
        
        final TransactionBuilder txBuilder = new TransactionBuilder(notary)
                .addOutputState(medicalRecordState, MedicalRecordContract.ID)
                .addCommand(txCommand);
        
        txBuilder.verify(getServiceHub());
        
        final SignedTransaction signedTx = getServiceHub().signInitialTransaction(txBuilder);
        
        return subFlow(new FinalityFlow(signedTx, Arrays.asList()));
    }
}
