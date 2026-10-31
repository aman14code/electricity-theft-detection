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

// ─── GET /api/dashboard/daily-detections — 7-day alert trend ─
router.get("/daily-detections", async (req, res) => {
  try {
    const meters = await Meter.find({ company: req.company.id }).select("_id");
    const meterIds = meters.map((m) => m._id);

    const since = new Date();
    since.setDate(since.getDate() - 7);

    const pipeline = await Alert.aggregate([
      {
        $match: {
          meter: { $in: meterIds },
          createdAt: { $gte: since },
        },
      },
      {
        $group: {
          _id: { $dayOfWeek: "$createdAt" },
          detections: { $sum: 1 },
        },
      },
      { $sort: { _id: 1 } },
    ]);

    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    // Fill all 7 days, even if 0
    const data = dayNames.map((day, i) => {
      const found = pipeline.find((p) => p._id === i + 1);
      return { day, detections: found ? found.detections : 0 };
    });

    res.json({ success: true, data });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── GET /api/dashboard/area-theft — theft cases by area/location ─
router.get("/area-theft", async (req, res) => {
  try {
    const meters = await Meter.find({ company: req.company.id }).select("_id location");
    const meterIds = meters.map((m) => m._id);

    const pipeline = await Alert.aggregate([
      {
        $match: {
          meter: { $in: meterIds },
          status: { $in: ["pending", "investigating"] },
        },
      },
      {
        $lookup: {
          from: "meters",
          localField: "meter",
          foreignField: "_id",
          as: "meterInfo",
        },
      },
      { $unwind: "$meterInfo" },
      {
        $group: {
          _id: "$meterInfo.location",
          cases: { $sum: 1 },
        },
      },
      { $sort: { cases: -1 } },
      { $limit: 8 },
    ]);

    const data = pipeline.map((p) => ({
      area: p._id || "Unknown",
      cases: p.cases,
    }));

    res.json({ success: true, data });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── GET /api/dashboard/risk-distribution — high/medium/low counts ─
router.get("/risk-distribution", async (req, res) => {
  try {
    const meters = await Meter.find({ company: req.company.id }).select("_id");
    const meterIds = meters.map((m) => m._id);

    const [high, medium, low] = await Promise.all([
      Alert.countDocuments({
        meter: { $in: meterIds },
        theftProbabilityScore: { $gte: 0.70 },
        status: { $in: ["pending", "investigating"] },
      }),
      Alert.countDocuments({
        meter: { $in: meterIds },
        theftProbabilityScore: { $gte: 0.30, $lt: 0.70 },
        status: { $in: ["pending", "investigating"] },
      }),
      Alert.countDocuments({
        meter: { $in: meterIds },
        theftProbabilityScore: { $lt: 0.30 },
        status: { $in: ["pending", "investigating"] },
      }),
    ]);

    res.json({
      success: true,
      data: [
        { name: "High Risk (>70%)", value: high },
        { name: "Medium Risk (30-70%)", value: medium },
        { name: "Low Risk (<30%)", value: low },
      ],
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// ─── GET /api/dashboard/monthly-recovery — estimated revenue recovery ─
router.get("/monthly-recovery", async (req, res) => {
  try {
    const meters = await Meter.find({ company: req.company.id }).select("_id");
    const meterIds = meters.map((m) => m._id);

    const since = new Date();
    since.setMonth(since.getMonth() - 6);

    const pipeline = await Alert.aggregate([
      {
        $match: {
          meter: { $in: meterIds },
          status: "resolved",
          createdAt: { $gte: since },
        },
      },
      {
        $group: {
          _id: {
            $dateToString: { format: "%Y-%m", date: "$createdAt" },
          },
          resolvedCount: { $sum: 1 },
          avgScore: { $avg: "$theftProbabilityScore" },
        },
      },
      { $sort: { _id: 1 } },
    ]);

    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const data = pipeline.map((p) => {
      const monthIdx = parseInt(p._id.split("-")[1]) - 1;
      // Estimate: each resolved case recovers ~₹4,500 avg * probability weight
      const estimatedRecovery = Math.round(p.resolvedCount * 4500 * (p.avgScore || 0.5));
      return {
        month: monthNames[monthIdx] || p._id,
        amount: estimatedRecovery,
        cases: p.resolvedCount,
      };
    });

    res.json({ success: true, data });
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
