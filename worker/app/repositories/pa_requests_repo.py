from app.config.db import get_db_conn
from app.utils.constants import PaRequestStatus

class PaRequestsRepository:

    def mark_evidence_ready(self, pa_request_id: int):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE core.pa_requests
            SET status = %s,
                modified_at = NOW(),
                modified_by = 'worker'
            WHERE id = %s
              AND status != %s
            """,
            (
                PaRequestStatus.EVIDENCE_READY,
                pa_request_id,
                PaRequestStatus.DECIDED,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()


    def mark_processing_failed(self, pa_request_id: int):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE core.pa_requests
            SET status = %s,
                modified_at = NOW(),
                modified_by = 'worker'
            WHERE id = %s
              AND status NOT IN (%s, %s)
            """,
            (
                PaRequestStatus.FAILED,
                pa_request_id,
                PaRequestStatus.DECIDED,
                PaRequestStatus.EVIDENCE_READY,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    def mark_needs_more_info(self, pa_request_id: int):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE core.pa_requests
            SET
              status = 'NEEDS_MORE_INFO',
              modified_at = NOW(),
              modified_by = 'worker'
            WHERE id = %s
              AND status <> 'NEEDS_MORE_INFO'
            """,
            (pa_request_id,),
        )

        conn.commit()
        cur.close()
        conn.close()
