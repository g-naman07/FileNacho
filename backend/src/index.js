// server.js
import express from "express";
import http from "http";
import cors from "cors";
import { setupSignaling } from "./signalling.js";

const app = express();
const allowedOrigins = (process.env.FRONTEND_URLS || "http://localhost:5173")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

app.use(
  cors({
    origin: allowedOrigins,
  })
);

const server = http.createServer(app);
setupSignaling(server);

const PORT = Number(process.env.PORT || 5000);

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
