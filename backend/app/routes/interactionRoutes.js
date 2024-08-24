import express from "express";
import interactionController from "../controllers/interactionController.js";

const router = express.Router();

router.get("/", interactionController.getLatestInteraction);
router.get(
  "/:billboardName",
  interactionController.getInteractionByBillboardName
);

export default router;
