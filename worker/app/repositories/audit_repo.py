from app.config.db import get_db_conn
from psycopg2.extras import Json

class AuditRepository:

    def log(
        self,
        pa_request_id: int,
        action: str,
        actor: str = "WORKER",
        metadata: dict | None = None,
    ):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO core.audit_logs
              (
                pa_request_id,
                actor,
                action,
                metadata,
                created_by,
                modified_by
              )
            VALUES
              (%s, %s, %s, %s, %s, %s)
            """,
            (
                pa_request_id,
                actor,
                action,
                Json(metadata) if metadata else None,
                actor,
                actor,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()
