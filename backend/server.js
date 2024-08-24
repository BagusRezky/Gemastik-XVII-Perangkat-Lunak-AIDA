import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import interactionRoutes from "./app/routes/interactionRoutes.js";
import mqttService from "./app/services/mqttService.js";
import db from "./config/db.js";

const app = express();

app.use(bodyParser.json());
app.use(cors());

// Connect to the database
db.connect((err) => {
  if (err) {
    throw err;
  }
  console.log("MySQL connected");
});

// Initialize MQTT service
mqttService.init();

app.use("/interactions", interactionRoutes);

app.listen(3000, () => {
  console.log("Server started on port 3000");
});
