import customErrorHandler from "../utils/custom.error";
import AuditService from "./service";
import { Request, Response } from "express";

export default class AuditController extends AuditService {
  public fetchAuditLogsController = async (req: Request, res: Response) => {
    try {
      const { pa_request_id, limit, page } = req.query;

      const data = await this.fetchAuditLogsService({
        pa_request_id: pa_request_id?.toString()!,
        limit: limit ? Number(limit) : 20,
        page: page ? Number(page) : 0,
      });

      res.status(200).send({
        success: true,
        data,
      });
    } catch (err) {
      customErrorHandler(res, err);
    }
  };
}
