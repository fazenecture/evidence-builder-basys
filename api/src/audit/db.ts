import db from "../config/postgres";
import { IFetchAuditLogsReqObj, IInsertAuditLogDbObj } from "./types/types";

export default class AuditDb {
  protected insertAuditLogDb = async (obj: IInsertAuditLogDbObj) => {
    const { pa_request_id, action, actor, metadata } = obj;

    await db.query(
      `
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
      ($1, $2, $3, $4, $5, $5)
    `,
      [pa_request_id, actor, action, metadata ?? null, actor],
    );
  };

  protected fetchAuditLogsDb = async (obj: IFetchAuditLogsReqObj) => {
    const { pa_request_id, limit, page } = obj;

    const offset = page * limit;

    const query = `
      WITH pa_request AS (
        SELECT id
        FROM core.pa_requests
        WHERE request_uuid = $1
      ),
      filtered_audit_logs AS (
        SELECT
          al.id,
          al.actor,
          al.action,
          al.metadata,
          al.created_at
        FROM core.audit_logs al
        JOIN pa_request pr
          ON al.pa_request_id = pr.id
      )
      SELECT
        id,
        actor,
        action,
        metadata,
        created_at
      FROM filtered_audit_logs
      ORDER BY created_at ASC
      LIMIT $2 OFFSET $3;`;

    const { rows } = await db.query(query, [pa_request_id, limit, offset]);

    return rows;
  };
}
