import { Router } from "express";
import DocumentsController from "./controller";

const router = Router();
const { uploadDocumentController } = new DocumentsController();

// POST /v1/documents/pa-requests/:id
router.post("/pa-requests/:id", uploadDocumentController);

export default router;
