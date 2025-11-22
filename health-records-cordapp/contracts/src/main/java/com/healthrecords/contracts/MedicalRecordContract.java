package com.healthrecords.contracts;

import com.healthrecords.states.MedicalRecordState;
import net.corda.core.contracts.CommandData;
import net.corda.core.contracts.CommandWithParties;
import net.corda.core.contracts.Contract;
import net.corda.core.identity.AbstractParty;
import net.corda.core.transactions.LedgerTransaction;

import java.util.stream.Collectors;

import static net.corda.core.contracts.ContractsDSL.requireSingleCommand;
import static net.corda.core.contracts.ContractsDSL.requireThat;

public class MedicalRecordContract implements Contract {
    public static final String ID = "com.healthrecords.contracts.MedicalRecordContract";

    @Override
    public void verify(LedgerTransaction tx) {
        final CommandWithParties<Commands> command = requireSingleCommand(tx.getCommands(), Commands.class);
        
        if (command.getValue() instanceof Commands.Create) {
            requireThat(require -> {
                require.using("No inputs should be consumed when creating a medical record.",
                        tx.getInputs().isEmpty());
                require.using("Only one output state should be created.",
                        tx.getOutputs().size() == 1);
                
                final MedicalRecordState output = tx.outputsOfType(MedicalRecordState.class).get(0);
                
                require.using("Patient ID must not be empty.",
                        output.getPatientId() != null && !output.getPatientId().isEmpty());
                require.using("Record title must not be empty.",
                        output.getTitle() != null && !output.getTitle().isEmpty());
                require.using("Record value must not be empty.",
                        output.getValue() != null && !output.getValue().isEmpty());
                require.using("All participants must be signers.",
                        command.getSigners().containsAll(output.getParticipants().stream()
                                .map(AbstractParty::getOwningKey)
                                .collect(Collectors.toList())));
                
                return null;
            });
        }
    }

    public interface Commands extends CommandData {
        class Create implements Commands {}
    }
}
