const mongoose = require("mongoose");

const meterSchema = new mongoose.Schema(
  {
    company: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "Company",
      required: true,
      index: true,
    },
    consumerName: {
      type: String,
      required: false,
      trim: true,
      default: "Unknown Consumer",
    },
    location: {
      type: String,
      required: [true, "Meter location is required"],
      trim: true,
    },
    areaCode: {
      type: String,
      required: false,
      trim: true,
      index: true,
    },
    substation: {
      type: String,
      required: false,
      trim: true,
      index: true,
    },
    consumerType: {
      type: String,
      enum: ["residential", "commercial"],
      default: "residential",
    },
    baselineConsumption: {
      type: Number,
      required: true,
      min: 0,
      comment: "Expected average hourly consumption in kWh",
    },
    isActive: {
      type: Boolean,
      default: true,
    },
  },
  { timestamps: true }
);

// Compound index for fast company-scoped queries
meterSchema.index({ company: 1, isActive: 1 });

module.exports = mongoose.model("Meter", meterSchema);
