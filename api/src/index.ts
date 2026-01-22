import * as dotenv from "dotenv";
dotenv.config();
import morgan from "morgan";
import { Request, Response, Application } from "express";
import express from "express";
import baseRouter from './routes/index.routes';

const app: Application = express();

app.use(express.json());
app.set("trust proxy", true);
app.use(morgan("dev"));

app.use("/api", baseRouter);

app.get("/health", (req: Request, res: Response) => {
  res.status(200).json({
    uptime: process.uptime(),
    hrtime: process.hrtime(),
  });
});

app.use("*", (req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    message: "NOT_FOUND",
  });
});

const PORT = process.env.PORT || 4000;

const init = async () => {
  app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
  });
};

init();
