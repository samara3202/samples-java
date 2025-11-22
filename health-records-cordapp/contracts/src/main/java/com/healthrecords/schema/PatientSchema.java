package com.healthrecords.schema;

import net.corda.core.schemas.MappedSchema;

public class PatientSchema extends MappedSchema {
    public PatientSchema() {
        super(PatientSchema.class, 1, java.util.Collections.singletonList(PatientSchemaV1.PersistentPatient.class));
    }
}
