package com.healthrecords.schema;

import net.corda.core.schemas.MappedSchema;

public class MedicalRecordSchema extends MappedSchema {
    public MedicalRecordSchema() {
        super(MedicalRecordSchema.class, 1, java.util.Collections.singletonList(MedicalRecordSchemaV1.PersistentMedicalRecord.class));
    }
}
