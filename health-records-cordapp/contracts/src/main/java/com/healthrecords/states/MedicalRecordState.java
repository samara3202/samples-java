package com.healthrecords.states;

import com.healthrecords.contracts.MedicalRecordContract;
import com.healthrecords.schema.MedicalRecordSchemaV1;
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

@BelongsToContract(MedicalRecordContract.class)
public class MedicalRecordState implements LinearState, QueryableState {
    private final String patientId;
    private final String title;
    private final String value;
    private final Party hospital;
    private final UniqueIdentifier linearId;

    public MedicalRecordState(String patientId,
                              String title,
                              String value,
                              Party hospital,
                              UniqueIdentifier linearId) {
        this.patientId = patientId;
        this.title = title;
        this.value = value;
        this.hospital = hospital;
        this.linearId = linearId;
    }

    public String getPatientId() {
        return patientId;
    }

    public String getTitle() {
        return title;
    }

    public String getValue() {
        return value;
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
        if (schema instanceof MedicalRecordSchemaV1) {
            return new MedicalRecordSchemaV1.PersistentMedicalRecord(
                    this.patientId,
                    this.title,
                    this.value,
                    this.hospital.getName().toString(),
                    this.linearId.getId());
        } else {
            throw new IllegalArgumentException("Unrecognised schema: " + schema);
        }
    }

    @Override
    public Iterable<MappedSchema> supportedSchemas() {
        return Arrays.asList(new MedicalRecordSchemaV1());
    }

    @Override
    public String toString() {
        return String.format("MedicalRecordState(patientId=%s, title=%s, value=%s, hospital=%s, linearId=%s)",
                patientId, title, value, hospital, linearId);
    }
}
