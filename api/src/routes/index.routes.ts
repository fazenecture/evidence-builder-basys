import { Router } from "express";
import paRequestRouter from "../pa-requests/routes";
import documentsRouter from "../documents/routes";
import auditRouter from "../audit/routes";

const router = Router();

router.use("/v1/pa-requests", paRequestRouter);
router.use("/v1/documents", documentsRouter);
router.use("/v1/audits", auditRouter);

export default router;
