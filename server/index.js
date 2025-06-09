const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
require("dotenv").config();
const authRoutes = require("./routes/auth");

const app = express();
app.use(cors());
app.use(express.json());
mongoose.connect(process.env.MONGO_URI);

app.use("/api/auth", authRoutes);
app.listen(5000, () => console.log("Auth server running on port 5000"));
