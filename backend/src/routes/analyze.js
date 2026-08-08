const express = require("express");
const axios = require("axios");
const Reading = require("../models/Reading");
const Meter = require("../models/Meter");
const Alert = require("../models/Alert");
const auth = require("../middleware/auth");

const router = express.Router();

router.use(auth);

const ML_URL = process.env.ML_SERVICE_URL || "http://localhost:8000";

/**
 * POST /api/analyze/bulk
 *
 * Runs anomaly analysis on ALL meters belonging to the authenticated company
 * in parallel (Promise.allSettled). Returns a summary with per-meter results.
 */
router.post("/bulk", async (req, res) => {
  try {
    const meters = await Meter.find({ company: req.company.id }).select("_id location consumerType baselineConsumption");

    if (meters.length === 0) {
      return res.json({ success: true, summary: { total: 0, anomalies: 0 }, results: [] });
    }

    const since = new Date();
    since.setDate(since.getDate() - 30);

    // Run all meter analyses in parallel
    const settledResults = await Promise.allSettled(
      meters.map(async (meter) => {
        const readings = await Reading.find({
          meter: meter._id,
          timestamp: { $gte: since },
        }).sort({ timestamp: 1 });

        if (readings.length === 0) {
          return { meter, skipped: true, reason: "No readings in last 30 days" };
        }

        const consumptions = readings.map((r) => r.consumptionKwh);
        const voltages = readings.map((r) => r.voltage);
        const currents = readings.map((r) => r.current);
        const powerFactors = readings.map((r) => r.powerFactor);
        const frequencies = readings.map((r) => r.frequency);
        const tamperCount = readings.filter((r) => r.tamperFlag).length;

        const stats = (arr) => {
          const n = arr.length;
          const mean = arr.reduce((a, b) => a + b, 0) / n;
          const std = Math.sqrt(arr.reduce((sum, v) => sum + (v - mean) ** 2, 0) / n);
          return { mean, std, min: Math.min(...arr), max: Math.max(...arr) };
        };

        const features = {
          consumption_stats: stats(consumptions),
          voltage_stats: stats(voltages),
          current_stats: stats(currents),
          power_factor_stats: stats(powerFactors),
          frequency_stats: stats(frequencies),
          tamper_ratio: tamperCount / readings.length,
          baseline_consumption: meter.baselineConsumption,
          consumer_type: meter.consumerType,
          reading_count: readings.length,
        };

        const payload = {
          meter_id: meter._id.toString(),
          features,
          readings: readings.map((r) => ({
            timestamp: r.timestamp.toISOString(),
            consumption_kwh: r.consumptionKwh,
            voltage: r.voltage,
            current: r.current,
            power_factor: r.powerFactor,
            frequency: r.frequency,
            tamper_flag: r.tamperFlag,
          })),
        };

        let mlResult;
        try {
          const response = await axios.post(`${ML_URL}/predict`, payload, { timeout: 15000 });
          mlResult = response.data;
        } catch {
          mlResult = computeFallbackHeuristic(readings, meter, features);
        }

        // Store alert if anomaly detected
        if (mlResult.anomaly_flag) {
          await Alert.create({
            meter: meter._id,
            timestamp: new Date(),
            theftProbabilityScore: mlResult.theft_probability,
            anomalyBreakdown: mlResult.anomaly_breakdown || {},
            anomalyFlag: true,
            status: "pending",
          });
        }

        return { meter, mlResult, anomalyDetected: mlResult.anomaly_flag };
      })
    );

    const results = settledResults.map((r, i) => {
      if (r.status === "rejected") {
        return { meter: { _id: meters[i]._id, location: meters[i].location }, error: r.reason?.message };
      }
      return r.value;
    });

    const anomalies = results.filter((r) => r?.anomalyDetected).length;

    res.json({
      success: true,
      summary: { total: meters.length, analyzed: results.filter((r) => !r.skipped && !r.error).length, anomalies },
      results,
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

/**
 * POST /api/analyze/:meterId
 *
 * 1. Fetch last 30 days of multi-dimensional readings
 * 2. Compute statistical features (mean, std, z-scores)
 * 3. Send enriched payload to the Python ML /predict endpoint
 * 4. If anomaly detected → store Alert with per-measure breakdown
 */
router.post("/:meterId", async (req, res) => {
  try {
    // ── Verify meter ownership ──────────────────────────
    const meter = await Meter.findOne({
      _id: req.params.meterId,
      company: req.company.id,
    });

    if (!meter) {
      return res
        .status(404)
        .json({ success: false, message: "Meter not found" });
    }

    // ── Fetch last 30 days of readings ──────────────────
    const since = new Date();
    since.setDate(since.getDate() - 30);

    const readings = await Reading.find({
      meter: meter._id,
      timestamp: { $gte: since },
    }).sort({ timestamp: 1 });

    if (readings.length === 0) {
      return res.status(400).json({
        success: false,
        message: "No readings found for the last 30 days",
      });
    }

    // ── Compute statistical features ────────────────────
    const consumptions = readings.map((r) => r.consumptionKwh);
    const voltages = readings.map((r) => r.voltage);
    const currents = readings.map((r) => r.current);
    const powerFactors = readings.map((r) => r.powerFactor);
    const frequencies = readings.map((r) => r.frequency);
    const tamperCount = readings.filter((r) => r.tamperFlag).length;

    const stats = (arr) => {
      const n = arr.length;
      const mean = arr.reduce((a, b) => a + b, 0) / n;
      const std = Math.sqrt(
        arr.reduce((sum, v) => sum + (v - mean) ** 2, 0) / n
      );
      const min = Math.min(...arr);
      const max = Math.max(...arr);
      return { mean, std, min, max };
    };

    const features = {
      consumption_stats: stats(consumptions),
      voltage_stats: stats(voltages),
      current_stats: stats(currents),
      power_factor_stats: stats(powerFactors),
      frequency_stats: stats(frequencies),
      tamper_ratio: tamperCount / readings.length,
      baseline_consumption: meter.baselineConsumption,
      consumer_type: meter.consumerType,
      reading_count: readings.length,
    };

    // ── Format readings for ML service ──────────────────
    const payload = {
      meter_id: meter._id.toString(),
      features,
      readings: readings.map((r) => ({
        timestamp: r.timestamp.toISOString(),
        consumption_kwh: r.consumptionKwh,
        voltage: r.voltage,
        current: r.current,
        power_factor: r.powerFactor,
        frequency: r.frequency,
        tamper_flag: r.tamperFlag,
      })),
    };

    // ── Call ML microservice ────────────────────────────
    let mlResult;
    try {
      const response = await axios.post(`${ML_URL}/predict`, payload, {
        timeout: 15000,
      });
      mlResult = response.data;
    } catch (mlErr) {
      console.error(
        "ML service error, using built-in fallback:",
        mlErr.message
      );
      // ── Built-in fallback heuristic (8 measures) ─────
      mlResult = computeFallbackHeuristic(readings, meter, features);
    }

    // ── Store alert if anomaly detected ─────────────────
    if (mlResult.anomaly_flag) {
      const alert = await Alert.create({
        meter: meter._id,
        timestamp: new Date(),
        theftProbabilityScore: mlResult.theft_probability,
        anomalyBreakdown: mlResult.anomaly_breakdown || {},
        anomalyFlag: true,
        status: "pending",
      });

      return res.json({
        success: true,
        anomalyDetected: true,
        alert,
        mlResult,
      });
    }

    res.json({
      success: true,
      anomalyDetected: false,
      mlResult,
      message: "No anomaly detected",
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

/**
 * Built-in fallback heuristic when the ML service is unavailable.
 * Uses 8 independent anomaly measures, each scored 0–1,
 * then combines them with weighted averaging for max accuracy.
 */
function computeFallbackHeuristic(readings, meter, features) {
  const scores = {
    consumptionDrop: 0,
    voltageAnomaly: 0,
    currentAnomaly: 0,
    powerFactorAnomaly: 0,
    frequencyDeviation: 0,
    tamperDetected: 0,
    patternIrregularity: 0,
    flatLineDetection: 0,
  };

  const { consumption_stats, voltage_stats, power_factor_stats, frequency_stats } = features;

  // ── 1. Consumption drop during peak hours ─────────────
  // Peak hours = 8 AM to 8 PM
  const peakReadings = readings.filter((r) => {
    const hour = new Date(r.timestamp).getUTCHours();
    return hour >= 8 && hour <= 20;
  });
  const zeroInPeak = peakReadings.filter((r) => r.consumptionKwh === 0).length;
  if (peakReadings.length > 0) {
    scores.consumptionDrop = Math.min(1, (zeroInPeak / peakReadings.length) * 5);
  }

  // ── 2. Voltage anomaly (outside 190–250V range) ──────
  const voltageOutliers = readings.filter(
    (r) => r.voltage < 190 || r.voltage > 250
  ).length;
  scores.voltageAnomaly = Math.min(1, (voltageOutliers / readings.length) * 3);

  // ── 3. Current anomaly (very low current with normal voltage)
  const suspiciousCurrent = readings.filter(
    (r) => r.current < 0.1 && r.voltage > 200 && r.consumptionKwh > 0
  ).length;
  scores.currentAnomaly = Math.min(
    1,
    (suspiciousCurrent / readings.length) * 4
  );

  // ── 4. Power factor anomaly (unusually low) ──────────
  const lowPF = readings.filter((r) => r.powerFactor < 0.5).length;
  scores.powerFactorAnomaly = Math.min(1, (lowPF / readings.length) * 3);

  // ── 5. Frequency deviation (outside 49.5–50.5 Hz) ───
  const freqOutliers = readings.filter(
    (r) => r.frequency < 49.0 || r.frequency > 51.0
  ).length;
  scores.frequencyDeviation = Math.min(
    1,
    (freqOutliers / readings.length) * 4
  );

  // ── 6. Tamper flag detection ──────────────────────────
  scores.tamperDetected = Math.min(1, features.tamper_ratio * 10);

  // ── 7. Pattern irregularity (high coefficient of variation)
  if (consumption_stats.mean > 0) {
    const cv = consumption_stats.std / consumption_stats.mean;
    scores.patternIrregularity = Math.min(1, Math.max(0, (cv - 0.5) / 1.5));
  }

  // ── 8. Flat-line detection (constant readings = tampered meter)
  const uniqueValues = new Set(readings.map((r) => r.consumptionKwh)).size;
  if (readings.length > 10) {
    const uniqueRatio = uniqueValues / readings.length;
    scores.flatLineDetection = Math.min(1, Math.max(0, (1 - uniqueRatio) * 2 - 0.5));
  }

  // ── Weighted combination ──────────────────────────────
  const weights = {
    consumptionDrop: 0.25,
    voltageAnomaly: 0.10,
    currentAnomaly: 0.15,
    powerFactorAnomaly: 0.10,
    frequencyDeviation: 0.05,
    tamperDetected: 0.20,
    patternIrregularity: 0.10,
    flatLineDetection: 0.05,
  };

  let weightedSum = 0;
  let totalWeight = 0;
  for (const [key, weight] of Object.entries(weights)) {
    weightedSum += scores[key] * weight;
    totalWeight += weight;
  }

  const theftProbability = Math.round((weightedSum / totalWeight) * 100) / 100;
  const anomalyFlag = theftProbability >= 0.30;

  return {
    theft_probability: theftProbability,
    anomaly_flag: anomalyFlag,
    anomaly_breakdown: scores,
    source: "fallback_heuristic",
  };
}

module.exports = router;
