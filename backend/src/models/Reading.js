const mongoose = require("mongoose");

/**
 * Reading schema — captures multi-dimensional smart meter telemetry
 * for maximum theft-detection accuracy.
 *
 * Measures captured:
 *  1. consumptionKwh  — active energy consumed
 *  2. voltage         — line voltage (V)
 *  3. current         — line current (A)
 *  4. powerFactor     — ratio of real to apparent power (0–1)
 *  5. frequency       — grid frequency in Hz (should be ~50 or ~60)
 *  6. tamperFlag      — hardware tamper indicator from the meter itself
 */
const readingSchema = new mongoose.Schema(
  {
    meter: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Meter",
      required: true,
      index: true,
    },
    timestamp: {
      type: Date,
      required: true,
      index: true,
    },
    // ─── Core consumption ───────────────────────────────
    consumptionKwh: {
      type: Number,
      required: true,
      min: 0,
    },
    // ─── Electrical measures for anomaly detection ──────
    voltage: {
      type: Number,
      required: true,
      min: 0,
    },
    current: {
      type: Number,
      default: 0,
      min: 0,
    },
    powerFactor: {
      type: Number,
      default: 1.0,
      min: 0,
      max: 1,
    },
    frequency: {
      type: Number,
      default: 50,
      min: 0,
    },
    tamperFlag: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: false, // we use our own `timestamp` field
  }
);

// Fast range queries: "all readings for meter X in the last 30 days"
readingSchema.index({ meter: 1, timestamp: -1 });

// Compound for aggregation pipelines
readingSchema.index({ meter: 1, timestamp: 1, consumptionKwh: 1 });

module.exports = mongoose.model("Reading", readingSchema);
