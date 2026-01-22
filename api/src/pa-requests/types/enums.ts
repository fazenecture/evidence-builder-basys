export enum PaRequestStatusEnum {
  CREATED = "created",
  PROCESSING = "processing",
  COMPLETE = "complete",
  FAILED = "failed",
}

export enum AuditAction {
  // PA lifecycle
  PA_CREATED = "pa_created",
  PA_STATUS_UPDATED = "pa_status_updated",
  PA_DECIDED = "pa_decided",

  // Document lifecycle
  DOCUMENT_UPLOADED = "document_uploaded",
  DOCUMENT_REPROCESSED = "document_reprocessed",
  DOCUMENT_PROCESSING_STARTED = "document_processing_started",
  DOCUMENT_PROCESSED = "document_processed",
  DOCUMENT_PROCESSING_FAILED = "document_processing_failed",

  // Evidence lifecycle
  EVIDENCE_PACK_CREATED = "evidence_pack_created",
  EVIDENCE_READY = "evidence_ready",

  // System / async
  JOB_ENQUEUED = "job_enqueued",
  JOB_RETRIED = "job_retried",
  JOB_SENT_TO_DLQ = "job_sent_to_dlq",
}
