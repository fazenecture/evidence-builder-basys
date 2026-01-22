import time
import uuid
from app.repositories.documents_repo import DocumentsRepository
from app.repositories.evidence_repo import EvidenceRepository
from app.utils.logger import logger
from app.utils.constants import AuditAction, DocumentStatus
from app.repositories.pa_requests_repo import PaRequestsRepository
from app.repositories.audit_repo import AuditRepository
from app.services.evidence_extractor import EvidenceExtractor
from app.services.policy_evaluator import PolicyEvaluator
from app.repositories.processing_jobs_repo import ProcessingJobsRepository


class DocumentProcessor:

    def __init__(self):
        self.documents_repo = DocumentsRepository()
        self.evidence_repo = EvidenceRepository()
        self.pa_requests_repo = PaRequestsRepository()
        self.audit_repo = AuditRepository()
        self.extractor = EvidenceExtractor()
        self.policy = PolicyEvaluator()
        self.processing_jobs_repo = ProcessingJobsRepository()

    def process(self, job: dict):
        logger.info("Starting document processing")
        document_id = job["document_id"]
        pa_request_id = job["pa_request_id"]
        job_uuid = job["job_uuid"]

        logger.info(f"Processing job_uuid: {job_uuid} for document_id: {document_id}")
        trace_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(f"Upserting processing job for document {document_id} {trace_id} {start_time}")

        attempt_count = 1
        # attempt_count = self.processing_jobs_repo.upsert_processing_job(
        #     job_uuid=job_uuid,
        #     document_id=document_id,
        #     trace_id=trace_id,
        # )

        logger.info(f"Processing document: {document_id}")

        try:
            logger.info(f"Fetching text for document {document_id}")
            text = self.documents_repo.fetch_document_text(document_id)
            logger.info(f"Fetched text for document {document_id}")
            if not text:
                raise Exception("Document text not found")

            # STEP B: Deterministic extraction
            logger.info(f"Extracting evidence from document {document_id}")
            evidence = self.extractor.extract(text)

            # STEP C: Policy evaluation
            logger.info(f"Evaluating policy for PA request {pa_request_id}")            
            policy_result = self.policy.evaluate_tka(evidence)

            # STEP D: Evidence pack (idempotent)
            logger.info(f"Creating/updating evidence pack for PA request {pa_request_id}")
            evidence_pack_id = self.evidence_repo.create_or_get_evidence_pack(
                pa_request_id
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # STEP E: Store extracted evidence + decision
            logger.info(f"Storing extracted evidence for evidence pack {evidence_pack_id}")
            self.evidence_repo.insert_extracted_evidence(
                evidence_pack_id=evidence_pack_id,
                diagnosis=evidence.get("diagnosis", {}).get("value"),
                imaging_present=evidence.get("imaging_present", {}).get("value"),
                therapy_attempted=evidence.get("conservative_therapy", {}).get("attempted"),
                functional_limitation=evidence.get("functional_limitation", {}).get("value"),
                missing_fields=evidence.get("missing_fields"),
                sources={
                    "diagnosis": evidence.get("diagnosis", {}).get("source"),
                    "conservative_therapy": evidence.get("conservative_therapy", {}).get("source"),
                    "imaging_present": evidence.get("imaging_present", {}).get("source"),
                    "functional_limitation": evidence.get("functional_limitation", {}).get("source"),
                },
                document_id=document_id
            )


            
            logger.info(f"Updating evidence pack decision for evidence pack {evidence_pack_id}")
            self.evidence_repo.update_evidence_pack_decision(
                evidence_pack_id=evidence_pack_id,
                decision=policy_result["decision"],
                explanation=policy_result["explanation"],
                sources={
                    "diagnosis": evidence.get("diagnosis", {}).get("source"),
                    "conservative_therapy": evidence.get("conservative_therapy", {}).get("source"),
                    "imaging_present": evidence.get("imaging_present", {}).get("source"),
                    "functional_limitation": evidence.get("functional_limitation", {}).get("source"),
                },
                metadata={
                    "missing_requirements": policy_result["missing_requirements"],
                    "attempt": attempt_count,
                    "latency_ms": latency_ms,
                    "trace_id": trace_id,
                    "policy": "TKA_v1",
                },
            )

            # Audit: evidence pack created
            logger.info(f"Logging audit for evidence pack {evidence_pack_id}")
            self.audit_repo.log(
                pa_request_id=pa_request_id,
                action=AuditAction.EVIDENCE_PACK_CREATED,
                metadata={
                    "evidence_pack_id": evidence_pack_id,
                    "decision": policy_result["decision"],
                },
            )

            # Update PA request status
            logger.info(f"Updating PA request {pa_request_id} status based on policy decision")
            if policy_result["decision"] == "APPROVE":
                self.pa_requests_repo.mark_evidence_ready(pa_request_id)
                self.audit_repo.log(
                    pa_request_id=pa_request_id,
                    action=AuditAction.EVIDENCE_READY,
                )
            else:
                self.pa_requests_repo.mark_needs_more_info(pa_request_id)
                self.audit_repo.log(
                    pa_request_id=pa_request_id,
                    action=AuditAction.PA_NEEDS_MORE_INFO,
                    metadata={
                        "missing": policy_result["missing_requirements"]
                    },
                )

            # Processing job success
            self.processing_jobs_repo.mark_success(job_uuid)

            logger.info(f"Document {document_id} processed successfully")

        except Exception as e:
            logger.error(f"Failed processing document {document_id}: {e}")

            self.documents_repo.update_document_status(
                document_id,
                DocumentStatus.FAILED,
            )

            self.pa_requests_repo.mark_processing_failed(pa_request_id)

            self.processing_jobs_repo.mark_failed(job_uuid, str(e))

            self.audit_repo.log(
                pa_request_id=pa_request_id,
                action=AuditAction.DOCUMENT_PROCESSING_FAILED,
                metadata={
                    "document_id": document_id,
                    "error": str(e),
                },
            )

            raise