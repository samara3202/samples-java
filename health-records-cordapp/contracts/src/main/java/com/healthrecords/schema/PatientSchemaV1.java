package com.healthrecords.schema;

import net.corda.core.schemas.MappedSchema;
import net.corda.core.schemas.PersistentState;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Table;
import java.util.UUID;

public class PatientSchemaV1 extends MappedSchema {
    public PatientSchemaV1() {
        super(PatientSchema.class, 1, java.util.Collections.singletonList(PersistentPatient.class));
    }
    
    @Override
    public String getMigrationResource() {
        return "patient.changelog-master";
    }

    @Entity
    @Table(name = "patient_states")
    public static class PersistentPatient extends PersistentState {
        @Column(name = "patient_id")
        private final String patientId;

        @Column(name = "name")
        private final String name;

        @Column(name = "age")
        private final Integer age;

        @Column(name = "hospital")
        private final String hospital;

        @Column(name = "linear_id")
        private final UUID linearId;

        public PersistentPatient(String patientId, String name, Integer age, String hospital, UUID linearId) {
            this.patientId = patientId;
            this.name = name;
            this.age = age;
            this.hospital = hospital;
            this.linearId = linearId;
        }

        public PersistentPatient() {
            this.patientId = null;
            this.name = null;
            this.age = null;
            this.hospital = null;
            this.linearId = null;
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

        public String getHospital() {
            return hospital;
        }

        public UUID getLinearId() {
            return linearId;
        }
    }
}
