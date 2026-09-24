const express = require("express");
const Meter = require("../models/Meter");
const Alert = require("../models/Alert");
const Reading = require("../models/Reading");
const auth = require("../middleware/auth");

const router = express.Router();

router.use(auth);

// ─── GET /api/dashboard/stats — high-level metrics ──────
router.get("/stats", async (req, res) => {
  try {
    const meters = await Meter.find({ company: req.company.id }).select("_id");
    const meterIds = meters.map((m) => m._id);

    const totalMeters = meters.length;
    const activeMeters = await Meter.countDocuments({
      company: req.company.id,
      isActive: true,
    });

    const activeAlerts = await Alert.countDocuments({
      meter: { $in: meterIds },
      status: { $in: ["pending", "investigating"] },
    });

    const resolvedAlerts = await Alert.countDocuments({
      meter: { $in: meterIds },
      status: "resolved",
    });

    // Average theft probability across pending alerts
    const avgProbResult = await Alert.aggregate([
      {
        $match: {
          meter: { $in: meterIds },
          status: { $in: ["pending", "investigating"] },
        },
      },
      { $group: { _id: null, avg: { $avg: "$theftProbabilityScore" } } },
    ]);
    const avgTheftProbability =
      avgProbResult.length > 0
        ? Math.round(avgProbResult[0].avg * 100) / 100
        : 0;

    res.json({
      success: true,
      data: {
        totalMeters,
        activeMeters,
        activeAlerts,
        resolvedAlerts,
        avgTheftProbability,
      },
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── GET /api/dashboard/consumption — 7-day aggregation ─
router.get("/consumption", async (req, res) => {
  try {
    const meters = await Meter.find({ company: req.company.id }).select("_id");
    const meterIds = meters.map((m) => m._id);

    const since = new Date();
    since.setDate(since.getDate() - 7);

    const consumption = await Reading.aggregate([
      {
        $match: {
          meter: { $in: meterIds },
          timestamp: { $gte: since },
        },
      },
      {
        $group: {
          _id: {
            $dateToString: { format: "%Y-%m-%d", date: "$timestamp" },
          },
          totalConsumption: { $sum: "$consumptionKwh" },
          avgVoltage: { $avg: "$voltage" },
          avgCurrent: { $avg: "$current" },
          avgPowerFactor: { $avg: "$powerFactor" },
          readingCount: { $sum: 1 },
        },
      },
      { $sort: { _id: 1 } },
    ]);

    res.json({
      success: true,
      data: consumption.map((d) => ({
        date: d._id,
        totalConsumption: Math.round(d.totalConsumption * 100) / 100,
        avgVoltage: Math.round(d.avgVoltage * 10) / 10,
        avgCurrent: Math.round(d.avgCurrent * 100) / 100,
        avgPowerFactor: Math.round(d.avgPowerFactor * 100) / 100,
        readingCount: d.readingCount,
      })),
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

const axios = require("axios");
const ML_URL = process.env.ML_SERVICE_URL || "http://localhost:8000";

// ─── GET /api/dashboard/ml-metrics — proxy ML service metrics ─
router.get("/ml-metrics", async (req, res) => {
  try {
    const response = await axios.get(`${ML_URL}/metrics`, { timeout: 5000 });
    res.json({ success: true, data: response.data });
  } catch (err) {
    // Try reading the file directly as fallback
    const path = require("path");
    const fs = require("fs");
    const metricsPath = path.join(__dirname, "..", "..", "..", "ml-service", "results", "evaluation_results.json");
    if (fs.existsSync(metricsPath)) {
      const data = JSON.parse(fs.readFileSync(metricsPath, "utf-8"));
      return res.json({ success: true, data });
    }
    res.status(502).json({ success: false, message: "ML service unavailable" });
  }
});

// ─── GET /api/dashboard/model-info — proxy ML model info ─
router.get("/model-info", async (req, res) => {
  try {
    const response = await axios.get(`${ML_URL}/model-info`, { timeout: 5000 });
    res.json({ success: true, data: response.data });
  } catch {
    res.status(502).json({ success: false, message: "ML service unavailable" });
  }
});

module.exports = router;
