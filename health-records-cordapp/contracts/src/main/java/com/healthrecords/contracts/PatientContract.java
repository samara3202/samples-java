package com.healthrecords.contracts;

import com.healthrecords.states.PatientState;
import net.corda.core.contracts.CommandData;
import net.corda.core.contracts.CommandWithParties;
import net.corda.core.contracts.Contract;
import net.corda.core.identity.AbstractParty;
import net.corda.core.transactions.LedgerTransaction;

import java.util.stream.Collectors;

import static net.corda.core.contracts.ContractsDSL.requireSingleCommand;
import static net.corda.core.contracts.ContractsDSL.requireThat;

public class PatientContract implements Contract {
    public static final String ID = "com.healthrecords.contracts.PatientContract";

    @Override
    public void verify(LedgerTransaction tx) {
        final CommandWithParties<Commands> command = requireSingleCommand(tx.getCommands(), Commands.class);
        
        if (command.getValue() instanceof Commands.Create) {
            requireThat(require -> {
                require.using("No inputs should be consumed when creating a patient record.",
                        tx.getInputs().isEmpty());
                require.using("Only one output state should be created.",
                        tx.getOutputs().size() == 1);
                
                final PatientState output = tx.outputsOfType(PatientState.class).get(0);
                
                require.using("Patient ID must not be empty.",
                        output.getPatientId() != null && !output.getPatientId().isEmpty());
                require.using("Patient name must not be empty.",
                        output.getName() != null && !output.getName().isEmpty());
                require.using("Patient age must be positive.",
                        output.getAge() != null && output.getAge() > 0);
                require.using("All participants must be signers.",
                        command.getSigners().containsAll(output.getParticipants().stream()
                                .map(AbstractParty::getOwningKey)
                                .collect(Collectors.toList())));
                
                return null;
            });
        } else if (command.getValue() instanceof Commands.Retrieve) {
            requireThat(require -> {
                require.using("At least one input state should exist for retrieval.",
                        !tx.getInputs().isEmpty());
                return null;
            });
        }
    }

    public interface Commands extends CommandData {
        class Create implements Commands {}
        class Retrieve implements Commands {}
    }
}
