import { IInsertPaRequestDbInput, IInsertPaRequestDbResponse } from "./types/types";
import db from "../config/postgres";

export default class PaRequestDb {
  protected insertPaRequestDb = async (
    params: IInsertPaRequestDbInput,
  ): Promise<IInsertPaRequestDbResponse> => {
    const { status, created_by } = params;

    const result = await db.query(
      `
      INSERT INTO core.pa_requests
        (status, created_by, modified_by)
      VALUES
        ($1, $2, $2)
      RETURNING request_uuid, id
      `,
      [status, created_by],
    );

    return result.rows[0] as unknown as IInsertPaRequestDbResponse;
  };

  protected fetchPaRequestByIdDb = async (id: number) => {
    const result = await db.query(
      `
        WITH latest_evidence_pack AS (
        SELECT 
            DISTINCT ON (pa_request_id)
            id,
            pa_request_id,
            status,
            decision,
            created_at
        FROM 
            core.evidence_packs
        ORDER BY 
            pa_request_id, created_at DESC
        )
        SELECT
            pr.id              AS pa_request_id,
            pr.request_uuid,
            pr.status           AS pa_status,
            pr.created_at       AS pa_created_at,

            lep.id              AS evidence_pack_id,
            lep.status          AS evidence_pack_status,
            lep.decision        AS evidence_pack_decision,
            lep.created_at      AS evidence_pack_created_at
        FROM 
            core.pa_requests pr
        LEFT JOIN 
            latest_evidence_pack lep
            ON lep.pa_request_id = pr.id
        WHERE 
            pr.request_uuid = $1;`,
      [id],
    );

    return result.rows[0] || null;
  };
}
