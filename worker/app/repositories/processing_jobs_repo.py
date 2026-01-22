from app.config.db import get_db_conn

class ProcessingJobsRepository:

    def upsert_processing_job(self, job_uuid: str, document_id: int, trace_id: str) -> int:
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO core.processing_jobs
            (job_uuid, document_id, status, attempt_count, trace_id,
            created_by, modified_by)
            VALUES
            (%s, %s, 'PROCESSING', 1, %s, 'worker', 'worker')
            ON CONFLICT (job_uuid)
            DO UPDATE SET
            attempt_count = core.processing_jobs.attempt_count + 1,
            status = 'PROCESSING',
            trace_id = EXCLUDED.trace_id,
            modified_at = NOW(),
            modified_by = 'worker'
            RETURNING attempt_count
            """,
            (job_uuid, document_id, trace_id),
        )

        row = cur.fetchone()
        if not row:
            raise Exception("Processing job upsert failed")

        conn.commit()
        cur.close()
        conn.close()

        return row[0]

    def mark_success(self, job_uuid: str):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE core.processing_jobs
            SET
              status = 'SUCCESS',
              modified_at = NOW(),
              modified_by = 'worker'
            WHERE job_uuid = %s
            """,
            (job_uuid,),
        )

        conn.commit()
        cur.close()
        conn.close()

    def mark_failed(self, job_uuid: str, error: str):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE core.processing_jobs
            SET
              status = 'FAILED',
              last_error = %s,
              modified_at = NOW(),
              modified_by = 'worker'
            WHERE job_uuid = %s
            """,
            (error, job_uuid),
        )

        conn.commit()
        cur.close()
        conn.close()


    def upsert_processing(
        self,
        job_uuid: str,
        document_id: int,
        status: str,
        attempt_count: int,
        last_error: str | None = None,
    ):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO core.processing_jobs
            (job_uuid, document_id, status, attempt_count, last_error,
            created_by, modified_by)
            VALUES
            (%s, %s, %s, %s, %s, 'worker', 'worker')
            ON CONFLICT (job_uuid)
            DO UPDATE SET
            status = EXCLUDED.status,
            attempt_count = EXCLUDED.attempt_count,
            last_error = EXCLUDED.last_error,
            modified_at = NOW(),
            modified_by = 'worker'
            """,
            (
                job_uuid,
                document_id,
                status,
                attempt_count,
                last_error,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()
