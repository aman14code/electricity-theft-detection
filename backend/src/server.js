require("dotenv").config();
const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const connectDB = require("./config/db");

// ─── Route imports ──────────────────────────────────────
const authRoutes = require("./routes/auth");
const meterRoutes = require("./routes/meters");
const readingRoutes = require("./routes/readings");
const alertRoutes = require("./routes/alerts");
const analyzeRoutes = require("./routes/analyze");
const dashboardRoutes = require("./routes/dashboard");

const app = express();

// ─── Middleware ──────────────────────────────────────────
app.use(cors());
app.use(express.json({ limit: "10mb" }));
app.use(morgan("dev"));

// ─── Health check ───────────────────────────────────────
app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// ─── Routes ─────────────────────────────────────────────
app.use("/api/auth", authRoutes);
app.use("/api/meters", meterRoutes);
app.use("/api/readings", readingRoutes);
app.use("/api/alerts", alertRoutes);
app.use("/api/analyze", analyzeRoutes);
app.use("/api/dashboard", dashboardRoutes);

// ─── Global error handler ───────────────────────────────
app.use((err, _req, res, _next) => {
  console.error("Unhandled error:", err);
  res.status(err.status || 500).json({
    success: false,
    message: err.message || "Internal Server Error",
  });
});

// ─── Start ──────────────────────────────────────────────
const PORT = process.env.PORT || 5000;

connectDB().then(() => {
  app.listen(PORT, () => {
    console.log(`⚡ Backend running on http://localhost:${PORT}`);
  });
});

module.exports = app;
