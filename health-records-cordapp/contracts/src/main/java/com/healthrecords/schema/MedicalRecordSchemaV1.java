package com.healthrecords.schema;

import net.corda.core.schemas.MappedSchema;
import net.corda.core.schemas.PersistentState;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Table;
import java.util.UUID;

public class MedicalRecordSchemaV1 extends MappedSchema {
    public MedicalRecordSchemaV1() {
        super(MedicalRecordSchema.class, 1, java.util.Collections.singletonList(PersistentMedicalRecord.class));
    }
    
    @Override
    public String getMigrationResource() {
        return "medical-record.changelog-master";
    }

    @Entity
    @Table(name = "medical_record_states")
    public static class PersistentMedicalRecord extends PersistentState {
        @Column(name = "patient_id")
        private final String patientId;

        @Column(name = "title")
        private final String title;

        @Column(name = "value")
        private final String value;

        @Column(name = "hospital")
        private final String hospital;

        @Column(name = "linear_id")
        private final UUID linearId;

        public PersistentMedicalRecord(String patientId, String title, String value, String hospital, UUID linearId) {
            this.patientId = patientId;
            this.title = title;
            this.value = value;
            this.hospital = hospital;
            this.linearId = linearId;
        }

        public PersistentMedicalRecord() {
            this.patientId = null;
            this.title = null;
            this.value = null;
            this.hospital = null;
            this.linearId = null;
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

        public String getHospital() {
            return hospital;
        }

        public UUID getLinearId() {
            return linearId;
        }
    }
}
