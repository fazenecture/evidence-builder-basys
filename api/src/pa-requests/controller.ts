import { REQUESTS } from "../utils/constants";
import customErrorHandler from "../utils/custom.error";
import PaService from "./service";
import { Request, Response } from "express";

export default class PaController extends PaService {
  public createPaRequestController = async (req: Request, res: Response) => {
    try {
      const actor = req.headers[REQUESTS.X_API_KEY] as string;
      const data = await this.createPaRequestService({ actor });

      return res.status(201).send({
        success: true,
        data,
      });
    } catch (err) {
      customErrorHandler(res, err);
    }
  };

  public fetchPaRequestByIdController = async (req: Request, res: Response) => {
    try {
      const { id } = req.params;

      const result = await this.fetchPaRequestByIdService(Number(id));

      return res.status(200).send({
        success: true,
        data: result,
      });
    } catch (error: any) {
      customErrorHandler(res, error);
    }
  };
}
