import { IInsertDocumentDbInput, IInsertDocumentDbOutput, IInsertDocumentTextDbInput, IResolvePaRequestDbOutput, IUpdatePARequestById } from "./types/types";
import db from '../config/postgres';

export default class DocumentsDb {

    protected resolvePaRequestByUuid = async (
    requestUuid: string
  ): Promise<IResolvePaRequestDbOutput | null> => {
    const result = await db.query(
      `
      SELECT id, request_uuid
      FROM core.pa_requests
      WHERE request_uuid = $1
      `,
      [requestUuid]
    );

    return result.rows[0] || null;
  };

  protected findDocumentByIdempotencyKey = async (
    paRequestId: number,
    idempotencyKey: string
  ): Promise<IInsertDocumentDbOutput | null> => {
    const result = await db.query(
      `
      SELECT id, document_uuid
      FROM core.documents
      WHERE pa_request_id = $1
        AND idempotency_key = $2
      `,
      [paRequestId, idempotencyKey]
    );

    return result.rows[0] || null;
  };

  protected insertDocument = async (
    params: IInsertDocumentDbInput
  ): Promise<IInsertDocumentDbOutput> => {
    const { pa_request_id, idempotency_key, status, created_by } = params;

    const result = await db.query(
      `
      INSERT INTO core.documents
        (pa_request_id, idempotency_key, status, created_by, modified_by)
      VALUES
        ($1, $2, $3, $4, $4)
      RETURNING id, document_uuid
      `,
      [pa_request_id, idempotency_key, status, created_by]
    );

    return result.rows[0];
  };

  protected insertDocumentText = async (
    params: IInsertDocumentTextDbInput
  ) => {
    const { document_id, text, created_by } = params;

    await db.query(
      `
      INSERT INTO phi.document_text
        (document_id, text, created_by, modified_by)
      VALUES
        ($1, $2, $3, $3)
      `,
      [document_id, text, created_by]
    );
  };

  protected updatePARequestById = async (obj: IUpdatePARequestById) => {
    const {pa_request_id, ...rest} = obj;
    const query = db.format(
      `UPDATE core.pa_requests
        SET ?
        WHERE id = $1
      `, rest
    );

    await db.query(query, [pa_request_id])
  }

}