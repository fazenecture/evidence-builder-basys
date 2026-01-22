import { REQUESTS } from "../utils/constants";
import customErrorHandler from "../utils/custom.error";
import DocumentService from "./service";
import { Request, Response } from "express";

export default class DocumentsController extends DocumentService {
  public uploadDocumentController = async (req: Request, res: Response) => {
    try {
      const { id: request_uuid } = req.params;
      const { document_text } = req.body;

      const actor = req.headers[REQUESTS.X_API_KEY] as string;
      const idempotency_key = req.headers[REQUESTS.IDEMPOTENCY_KEY] as string;

      const result = await this.uploadDocumentService({
        request_uuid,
        document_text,
        idempotency_key,
        actor,
      });

      return res.status(201).send({
        success: true,
        data: result,
      });
    } catch (error: any) {
      return customErrorHandler(res, error);
    }
  };
}
