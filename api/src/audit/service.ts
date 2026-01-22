import AuditHelper from "./helper";
import { IFetchAuditLogsReqObj } from "./types/types";

export default class AuditService extends AuditHelper {
  protected fetchAuditLogsService = async (obj: IFetchAuditLogsReqObj) => {
    const data = await this.fetchAuditLogsDb(obj);

    return data;
  };
}
