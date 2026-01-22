import logger from "../utils/logger";
import AuditDb from "./db";
import { IInsertAuditLogDbObj } from "./types/types";

export default class AuditHelper extends AuditDb {
  public createAuditLog = async (obj: IInsertAuditLogDbObj) => {
    try {
      await this.insertAuditLogDb(obj);
    } catch (err: any) {
      logger.error(`createAuditLog: Error creating the audit log`, err);
    }
  };
}
