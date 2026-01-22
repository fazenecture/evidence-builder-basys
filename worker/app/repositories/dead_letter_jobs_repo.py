from app.config.db import get_db_conn
from psycopg2.extras import Json

class DeadLetterJobsRepository:

    def insert(
        self,
        job_uuid,
        document_id,
        reason,
        payload,
        actor="worker",
    ):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO core.dead_letter_jobs
              (
                job_uuid,
                document_id,
                reason,
                payload,
                created_by,
                modified_by
              )
            VALUES
              (%s, %s, %s, %s, %s, %s)
            """,
            (
                job_uuid,
                document_id,
                reason,
                Json(payload),
                actor,
                actor,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()
