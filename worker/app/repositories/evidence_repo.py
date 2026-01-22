from app.config.db import get_db_conn
from app.utils.constants import EvidencePackStatus
from psycopg2.extras import Json
from app.utils.logger import logger

class EvidenceRepository:

    def create_evidence_pack(self, pa_request_id: int) -> int:
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO core.evidence_packs
              (pa_request_id, status, created_by, modified_by)
            VALUES
              (%s, %s, 'worker', 'worker')
            RETURNING id
            """,
            (pa_request_id, EvidencePackStatus.CREATED)
        )

        pack_id = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()

        return pack_id

    def insert_extracted_evidence(
        self,
        evidence_pack_id: int,
        diagnosis: str | None,
        imaging_present: bool | None,
        therapy_attempted: bool | None,
        functional_limitation: bool | None,
        missing_fields: dict | None,
        sources: dict | None,
        document_id: str,
    ):
        conn = get_db_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO phi.extracted_evidence
            (
                evidence_pack_id,
                diagnosis,
                imaging_present,
                therapy_attempted,
                functional_limitation,
                missing_fields,
                sources,
                document_id,
                created_by,
                modified_by
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s,'worker', 'worker')
            """,
            (
                evidence_pack_id,
                diagnosis,
                imaging_present,
                therapy_attempted,
                functional_limitation,
                Json(missing_fields),
                Json(sources),
                document_id
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    def update_evidence_pack_decision(
        self,
        evidence_pack_id: int,
        decision: str,
        explanation: str,
        sources: dict,
        metadata: dict,
    ):
        
        # Finalizes the evidence pack with decision + audit metadata
        conn = get_db_conn()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                UPDATE core.evidence_packs
                SET
                    status = 'finalized',
                    decision = %s,
                    explanation = %s,
                    sources = %s,
                    metadata = %s,
                    modified_at = NOW(),
                    modified_by = 'worker'
                WHERE id = %s
                """,
                (
                    decision,
                    explanation,
                    Json(sources),
                    Json(metadata),
                    evidence_pack_id,
                ),
            )

            if cur.rowcount == 0:
                raise Exception(
                    f"Evidence pack {evidence_pack_id} not found"
                )

            conn.commit()

        except Exception as e:
            conn.rollback()
            logger.error(
                f"Failed to update evidence pack decision: {e}"
            )
            raise
        finally:
            cur.close()
            conn.close()

    def create_or_get_evidence_pack(self, pa_request_id: int) -> int:
        conn = get_db_conn()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO core.evidence_packs
                (pa_request_id, created_by, modified_by)
                VALUES
                (%s, 'worker', 'worker')
                ON CONFLICT (pa_request_id)
                DO UPDATE SET
                pa_request_id = EXCLUDED.pa_request_id
                RETURNING id
                """,
                (pa_request_id,),
            )

            logger.info(f"Fetching evidence pack id for pa_request_id {pa_request_id}")
            row = cur.fetchone()
            if not row:
                logger.error(f"Failed to fetch evidence_pack_id for pa_request_id {pa_request_id}")
                raise Exception("Failed to fetch evidence_pack_id")

            conn.commit()
            logger.info(f"Fetched evidence pack id {row} for pa_request_id {pa_request_id}")
            return row["id"] if isinstance(row, dict) else row[0]

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create/get evidence pack: {e}")
            raise
        finally:
            cur.close()
            conn.close()
