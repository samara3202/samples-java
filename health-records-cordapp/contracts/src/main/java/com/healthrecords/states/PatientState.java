package com.healthrecords.states;

import com.healthrecords.contracts.PatientContract;
import com.healthrecords.schema.PatientSchemaV1;
import net.corda.core.contracts.BelongsToContract;
import net.corda.core.contracts.LinearState;
import net.corda.core.contracts.UniqueIdentifier;
import net.corda.core.identity.AbstractParty;
import net.corda.core.identity.Party;
import net.corda.core.schemas.MappedSchema;
import net.corda.core.schemas.PersistentState;
import net.corda.core.schemas.QueryableState;

import java.util.Arrays;
import java.util.List;

@BelongsToContract(PatientContract.class)
public class PatientState implements LinearState, QueryableState {
    private final String patientId;
    private final String name;
    private final Integer age;
    private final Party hospital;
    private final UniqueIdentifier linearId;

    public PatientState(String patientId,
                        String name,
                        Integer age,
                        Party hospital,
                        UniqueIdentifier linearId) {
        this.patientId = patientId;
        this.name = name;
        this.age = age;
        this.hospital = hospital;
        this.linearId = linearId;
    }

    public String getPatientId() {
        return patientId;
    }

    public String getName() {
        return name;
    }

    public Integer getAge() {
        return age;
    }

    public Party getHospital() {
        return hospital;
    }

    @Override
    public UniqueIdentifier getLinearId() {
        return linearId;
    }

    @Override
    public List<AbstractParty> getParticipants() {
        return Arrays.asList(hospital);
    }

    @Override
    public PersistentState generateMappedObject(MappedSchema schema) {
        if (schema instanceof PatientSchemaV1) {
            return new PatientSchemaV1.PersistentPatient(
                    this.patientId,
                    this.name,
                    this.age,
                    this.hospital.getName().toString(),
                    this.linearId.getId());
        } else {
            throw new IllegalArgumentException("Unrecognised schema: " + schema);
        }
    }

    @Override
    public Iterable<MappedSchema> supportedSchemas() {
        return Arrays.asList(new PatientSchemaV1());
    }

    @Override
    public String toString() {
        return String.format("PatientState(patientId=%s, name=%s, age=%d, hospital=%s, linearId=%s)",
                patientId, name, age, hospital, linearId);
    }
}
