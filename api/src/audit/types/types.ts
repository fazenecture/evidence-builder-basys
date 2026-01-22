export type IInsertAuditLogDbObj = {
  pa_request_id: number;
  actor: string;
  action: string;
  metadata?: object;
}

export type IFetchAuditLogsReqObj = {
  pa_request_id: string;
  limit: number;
  page: number;
}