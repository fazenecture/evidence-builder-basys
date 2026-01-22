import moment from "moment";
import redis from "../config/redis";
import ErrorHandler from "../utils/error.handler";
import DocumentsHelper from "./helper";
import { DocumentStatusEnum } from "./types/enums";
import {
  IUploadDocumentServiceInput,
  IUploadDocumentServiceOutput,
} from "./types/types";
import { AuditAction, PaRequestStatusEnum } from "../pa-requests/types/enums";
import AuditHelper from "../audit/helper";

export default class DocumentService extends DocumentsHelper {
  paAuditHelper: AuditHelper;

  constructor() {
    super();
    this.paAuditHelper = new AuditHelper();
  }

  public uploadDocumentService = async (
    params: IUploadDocumentServiceInput,
  ): Promise<IUploadDocumentServiceOutput> => {
    const { request_uuid, document_text, idempotency_key, actor } = params;

    if (!actor) {
      throw new ErrorHandler({
        status_code: 401,
        message: "Unauthorized",
      });
    }

    // 1️⃣ Resolve PA request
    const paRequest = await this.resolvePaRequestByUuid(request_uuid);

    if (!paRequest) {
      throw new ErrorHandler({
        status_code: 404,
        message: "PA request not found",
      });
    }

    // 2️⃣ Idempotency check
    const existingDocument = await this.findDocumentByIdempotencyKey(
      paRequest.id,
      idempotency_key,
    );

    if (existingDocument) {
      return {
        document_id: existingDocument.document_uuid,
        status: DocumentStatusEnum.PROCESSING,
      };
    }

    // 3️⃣ Create document metadata
    const document = await this.insertDocument({
      pa_request_id: paRequest.id,
      idempotency_key,
      status: this.getInitialStatus(),
      created_by: actor,
    });

    // 4️⃣ Insert PHI text
    await this.insertDocumentText({
      document_id: document.id,
      text: document_text,
      created_by: actor,
    });

    await this.updatePARequestById({
      pa_request_id: paRequest.id,
      modified_at: moment().format(),
      modified_by: actor,
      status: PaRequestStatusEnum.PROCESSING,
    });

    await this.paAuditHelper.createAuditLog({
      pa_request_id: paRequest.id,
      actor: `USER:${actor ?? "anonymous"}`,
      action: AuditAction.PA_CREATED,
      metadata: {
        document_id: document.id,
      },
    });

    // 5️⃣ Publish async job
    const jobPayload = {
      job_uuid: this.generateJobUuid(),
      document_id: document.id,
      document_uuid: document.document_uuid,
      pa_request_id: paRequest.id,
      request_uuid,
    };

    await redis.lpush("document_processing_queue", JSON.stringify(jobPayload));

    return {
      document_id: document.document_uuid,
      status: DocumentStatusEnum.PROCESSING,
    };
  };
}
