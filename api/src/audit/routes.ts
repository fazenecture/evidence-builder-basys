import { Router } from "express";
import AuditController from "./controller";

const router = Router();
const { fetchAuditLogsController } = new AuditController();

// GET /v1/audit/:pa_request_id
router.get("/:pa_request_id", fetchAuditLogsController);

export default router;
