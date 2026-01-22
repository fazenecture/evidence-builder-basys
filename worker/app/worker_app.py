import json
import time
import os

from app.config.redis import get_redis_client
from app.services.document_processor import DocumentProcessor
from app.repositories.audit_repo import AuditRepository
from app.utils.logger import logger
from app.utils.constants import AuditAction
from app.repositories.processing_jobs_repo import ProcessingJobsRepository
from app.repositories.dead_letter_jobs_repo import DeadLetterJobsRepository
import uuid



class WorkerApp:
    def __init__(self):
        self.redis = get_redis_client()
        self.processor = DocumentProcessor()
        self.audit_repo = AuditRepository()
        self.processing_repo = ProcessingJobsRepository()
        self.dead_letter_repo = DeadLetterJobsRepository()

        self.queue = os.getenv("QUEUE_NAME", "document_processing_queue")
        self.dlq = os.getenv("DLQ_NAME", "document_processing_dlq")
        self.max_retries = int(os.getenv("MAX_JOB_RETRIES", 3))

    def consume(self):
        logger.info("🚀 Worker started")

        while True:
            try:
                _, payload = self.redis.brpop(self.queue)
                job = json.loads(payload)
                self.handle_job(job)
            except Exception as e:
                logger.critical(f"Worker loop error: {e}")
                time.sleep(2)

    def handle_job(self, job: dict):
        attempt = job.get("attempt", 1)
        document_id = job.get("document_id")
        pa_request_id = job.get("pa_request_id")

        logger.info(
            f"Processing document={document_id}, attempt={attempt}"
        )

        job_uuid = job.get("job_uuid") or str(uuid.uuid4())
        job["job_uuid"] = job_uuid

        
        logger.info(f"Upserting processing job for document {document_id}, attempt {attempt}")
        self.processing_repo.upsert_processing(
            job_uuid=job_uuid,
            document_id=document_id,
            status="processing",
            attempt_count=attempt,
        )

        try:
            self.processor.process(job)

            self.processing_repo.upsert_processing(
                job_uuid=job_uuid,
                document_id=document_id,
                status="success",
                attempt_count=attempt,
            )

        except Exception as e:
            logger.error(
                f"Error processing document={document_id}, "
                f"attempt={attempt}, error={e}"
            )
            self.retry_or_dlq(job, attempt, document_id, pa_request_id, e)

    def retry_or_dlq(
        self,
        job: dict,
        attempt: int,
        document_id: int,
        pa_request_id: int,
        error: Exception,
    ):
        if attempt >= self.max_retries:
            self.send_to_dlq(job, document_id, pa_request_id, error)
        else:
            self.retry_job(job, attempt, document_id, pa_request_id)

    def retry_job(
        self,
        job: dict,
        attempt: int,
        document_id: int,
        pa_request_id: int,
    ):
        job["attempt"] = attempt + 1
        self.redis.lpush(self.queue, json.dumps(job))


        self.processing_repo.upsert_processing(
            job_uuid=job["job_uuid"],
            document_id=document_id,
            status="failed",
            attempt_count=attempt,
            last_error="Retrying job",
        )

        self.audit_repo.log(
            pa_request_id=pa_request_id,
            action=AuditAction.JOB_RETRIED,
            metadata={
                "document_id": document_id,
                "attempt": attempt + 1,
            },
        )

        logger.warning(
            f"Retrying document={document_id}, attempt={attempt + 1}"
        )

    def send_to_dlq(
        self,
        job: dict,
        document_id: int,
        pa_request_id: int,
        error: Exception,
    ):
        self.redis.lpush(
            self.dlq,
            json.dumps(
                {
                    **job,
                    "error": str(error),
                    "failed_at": time.time(),
                }
            ),
        )

        self.audit_repo.log(
            pa_request_id=pa_request_id,
            action=AuditAction.JOB_SENT_TO_DLQ,
            metadata={
                "document_id": document_id,
                "attempts": job.get("attempt", 1),
                "error": str(error),
            },
        )

        self.processing_repo.upsert_processing(
            job_uuid=job["job_uuid"],
            document_id=document_id,
            status="FAILED",
            attempt_count=job.get("attempt", 1),
            last_error=str(error),
        )

        self.dead_letter_repo.insert(
            job_uuid=job["job_uuid"],
            document_id=document_id,
            reason=str(error),
            payload=job,
        )

        logger.error(
            f"Document={document_id} sent to DLQ after "
            f"{job.get('attempt', 1)} attempts"
        )
