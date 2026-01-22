from app.config.db import get_db_conn

class DocumentsRepository:

    def fetch_document_text(self, document_id: int):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT text
            FROM phi.document_text
            WHERE document_id = %s
            """,
            (document_id,)
        )

        row = cur.fetchone()
        cur.close()
        conn.close()

        return row["text"] if row else None

    def update_document_status(self, document_id: int, status: str):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE core.documents
            SET status = %s,
                modified_at = NOW(),
                modified_by = 'worker'
            WHERE id = %s
            """,
            (status, document_id)
        )

        conn.commit()
        cur.close()
        conn.close()
