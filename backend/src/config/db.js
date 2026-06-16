const mongoose = require("mongoose");

const connectDB = async () => {
  const uri = process.env.MONGO_URI || "mongodb://localhost:27017/theft_detection";

  try {
    const conn = await mongoose.connect(uri);
    console.log(`✅ MongoDB connected: ${conn.connection.host}`);
  } catch (err) {
    console.error("❌ MongoDB connection error:", err.message);
    // Retry after 5 seconds
    console.log("⏳ Retrying in 5 seconds…");
    await new Promise((r) => setTimeout(r, 5000));
    return connectDB();
  }

  mongoose.connection.on("disconnected", () => {
    console.warn("⚠️  MongoDB disconnected — attempting reconnect…");
  });

  mongoose.connection.on("error", (err) => {
    console.error("MongoDB runtime error:", err.message);
  });
};

module.exports = connectDB;
