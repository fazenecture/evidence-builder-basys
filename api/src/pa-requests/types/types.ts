export type ICreatePaRequestValidatedReq = {
  actor: string;
};

export type ICreatePaRequestServiceInput = {
  actor: string;
};

export type ICreatePaRequestServiceOutput = {
  request_id: string;
};

export type IInsertPaRequestDbInput = {
  status: string;
  created_by: string;
};

export type IInsertPaRequestDbResponse = {
  request_uuid: string;
  id: number
}

