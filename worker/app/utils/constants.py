class DocumentStatus:
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class EvidencePackStatus:
    CREATED = "created"
    FINALIZED = "finalized"

class AuditAction:
    PA_CREATED = "pa_created"
    PA_STATUS_UPDATED = "pa_status_updated"
    PA_DECIDED = "pa_decided"

    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_REPROCESSED = "document_reprocessed"
    DOCUMENT_PROCESSING_STARTED = "document_processing_started"
    DOCUMENT_PROCESSED = "document_processed"
    DOCUMENT_PROCESSING_FAILED = "document_processing_failed"

    EVIDENCE_PACK_CREATED = "evidence_pack_created"
    EVIDENCE_READY = "evidence_ready"

    JOB_ENQUEUED = "job_enqueued"
    JOB_RETRIED = "job_retried"
    JOB_SENT_TO_DLQ = "job_sent_to_dlq"
    PA_NEEDS_MORE_INFO = "pa_needs_more_info"
    

class PaRequestStatus:
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    EVIDENCE_READY = "evidence_ready"
    DECIDED = "decided"
    FAILED = 'failed'
