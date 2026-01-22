import { PaRequestStatusEnum } from "../../pa-requests/types/enums";

export type IUploadDocumentServiceInput = {
  request_uuid: string;
  document_text: string;
  idempotency_key: string;
  actor: string;
};

export type IUploadDocumentServiceOutput = {
  document_id: string; // document_uuid (external)
  status: string;
};

export type IResolvePaRequestDbOutput = {
  id: number;           // internal PK
  request_uuid: string; // external
};

export type IInsertDocumentDbInput = {
  pa_request_id: number;
  idempotency_key: string;
  status: string;
  created_by: string;
};

export type IInsertDocumentDbOutput = {
  id: number;
  document_uuid: string;
};

export type IInsertDocumentTextDbInput = {
  document_id: number;
  text: string;
  created_by: string;
};

export type IDocumentProcessingJobPayload = {
  job_uuid: string;
  document_id: number;
  document_uuid: string;
  pa_request_id: number;
  request_uuid: string;
};

export type IUpdatePARequestById = {
  pa_request_id: number;
  modified_by: string;
  modified_at: string;

  status?: PaRequestStatusEnum;
}