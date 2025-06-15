const router = require("express").Router();
const User = require("../models/User");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");

// Signup
router.post("/signup", async (req, res) => {
  const hashed = await bcrypt.hash(req.body.password, 10);
  const user = new User({ ...req.body, password: hashed });
  await user.save();
  res.status(201).json({ msg: "User created" });
});

// Login
router.post("/login", async (req, res) => {
  const user = await User.findOne({ username: req.body.username});
  console.log("here")

  if (!user || !await bcrypt.compare(req.body.password, user.password)) {
    return res.status(400).json({ msg: "Invalid credentials" });
  }
  const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET);
  res.json({ token });
});

// JWT verification middleware
function verifyToken(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) return res.status(401).json({ msg: "No token" });
  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({ msg: "Token invalid" });
  }
}

// Get current user info (/me)
router.get('/me', verifyToken, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('username email');
    if (!user) return res.status(404).json({ msg: "User not found" });
    res.json({ username: user.username, email: user.email });
  } catch (err) {
    res.status(500).json({ msg: "Server error" });
  }
});

module.exports = router;