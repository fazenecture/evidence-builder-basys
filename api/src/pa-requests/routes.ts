import { Router } from "express";
import PaController from "./controller";

const router = Router();

const { createPaRequestController, fetchPaRequestByIdController } =
  new PaController();

// POST /api/v1/pa-requests
router.post("/", createPaRequestController);

// GET /api/v1/pa-requests/:id
router.get("/:id", fetchPaRequestByIdController);

export default router;
