const mongoose = require("mongoose");

const alertSchema = new mongoose.Schema(
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
    },
    theftProbabilityScore: {
      type: Number,
      required: true,
      min: 0,
      max: 1,
    },
    // ─── Breakdown of individual detection measures ─────
    anomalyBreakdown: {
      consumptionDrop: { type: Number, default: 0 },      // score 0–1
      voltageAnomaly: { type: Number, default: 0 },        // score 0–1
      currentAnomaly: { type: Number, default: 0 },        // score 0–1
      powerFactorAnomaly: { type: Number, default: 0 },    // score 0–1
      frequencyDeviation: { type: Number, default: 0 },    // score 0–1
      tamperDetected: { type: Number, default: 0 },        // score 0–1
      patternIrregularity: { type: Number, default: 0 },   // score 0–1
      flatLineDetection: { type: Number, default: 0 },     // score 0–1
    },
    anomalyFlag: {
      type: Boolean,
      default: false,
    },
    status: {
      type: String,
      enum: ["pending", "investigating", "resolved"],
      default: "pending",
    },
  },
  { timestamps: true }
);

// Fast company-level queries via populated meter
alertSchema.index({ status: 1, createdAt: -1 });

module.exports = mongoose.model("Alert", alertSchema);
