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
    
    private final Step GENERATING_TRANSACTION = new Step("Generating transaction for medical record.");
    private final Step VERIFYING_TRANSACTION = new Step("Verifying contract constraints.");
    private final Step SIGNING_TRANSACTION = new Step("Signing transaction with our private key.");
    private final Step FINALISING_TRANSACTION = new Step("Obtaining notary signature and recording transaction.") {
        @Override
        public ProgressTracker childProgressTracker() {
            return FinalityFlow.Companion.tracker();
        }
    };
    
    private final ProgressTracker progressTracker = new ProgressTracker(
            GENERATING_TRANSACTION,
            VERIFYING_TRANSACTION,
            SIGNING_TRANSACTION,
            FINALISING_TRANSACTION
    );
    
    public AddMedicalRecordFlow(String patientId, String title, String value) {
        this.patientId = patientId;
        this.title = title;
        this.value = value;
    }
    
    @Override
    public ProgressTracker getProgressTracker() {
        return progressTracker;
    }
    
    @Suspendable
    @Override
    public SignedTransaction call() throws FlowException {
        final Party notary = getServiceHub().getNetworkMapCache()
                .getNotary(CordaX500Name.parse("O=Notary,L=London,C=GB"));
        
        progressTracker.setCurrentStep(GENERATING_TRANSACTION);
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
        
        progressTracker.setCurrentStep(VERIFYING_TRANSACTION);
        txBuilder.verify(getServiceHub());
        
        progressTracker.setCurrentStep(SIGNING_TRANSACTION);
        final SignedTransaction signedTx = getServiceHub().signInitialTransaction(txBuilder);
        
        progressTracker.setCurrentStep(FINALISING_TRANSACTION);
        return subFlow(new FinalityFlow(signedTx, Arrays.asList()));
    }
}
