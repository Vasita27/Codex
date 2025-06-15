const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
require("dotenv").config();
const authRoutes = require("./routes/auth");

const app = express();
app.use(cors());
app.use(express.json());

// Connect to MongoDB Atlas (or Compass, if your .env points to local MongoDB)
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("Connected to MongoDB Atlas"))
  .catch(err => console.error("MongoDB connection error:", err));

// Auth routes
app.use("/api/auth", authRoutes);

app.listen(5000, () => console.log("Auth server running on port 5000"));