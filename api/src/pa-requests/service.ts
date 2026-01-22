import AuditHelper from "../audit/helper";
import { ERROR_MESSAGE } from "../utils/constants";
import ErrorHandler from "../utils/error.handler";
import PaHelper from "./helper";
import { AuditAction } from "./types/enums";
import {
  ICreatePaRequestServiceInput,
  ICreatePaRequestServiceOutput,
} from "./types/types";

export default class PaService extends PaHelper {
  paAuditHelper: AuditHelper;

  constructor() {
    super();
    this.paAuditHelper = new AuditHelper();
  }

  protected createPaRequestService = async (
    params: ICreatePaRequestServiceInput,
  ): Promise<ICreatePaRequestServiceOutput> => {
    const { actor } = params;

    if (!actor) {
      throw new ErrorHandler({
        status_code: 401,
        message: ERROR_MESSAGE.UNAUTHORIZED,
      });
    }

    const insertData = await this.insertPaRequestDb({
      status: this.getInitialStatus(),
      created_by: actor,
    });

    await this.paAuditHelper.createAuditLog({
      pa_request_id: insertData.id,
      actor: `USER:${actor ?? "anonymous"}`,
      action: AuditAction.PA_CREATED,
    });

    return {
      request_id: insertData.request_uuid,
    };
  };

  protected fetchPaRequestByIdService = async (id: number) => {
    const pa = await this.fetchPaRequestByIdDb(id);

    if (!pa) {
      throw new ErrorHandler({
        status_code: 400,
        message: ERROR_MESSAGE.PA_REQUEST_NOT_FOUND,
      });
    }

    return {
      id: pa.request_uuid,
      status: pa.pa_status,
      created_at: pa.pa_created_at,
      latest_evidence_pack: pa.evidence_pack_id
        ? {
            id: pa.evidence_pack_id,
            status: pa.evidence_pack_status,
            decision: pa.evidence_pack_decision,
            created_at: pa.evidence_pack_created_at,
          }
        : null,
    };
  };
}
