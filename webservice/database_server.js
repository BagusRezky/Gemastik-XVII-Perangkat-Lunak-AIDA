import express from "express";
import mysql from "mysql";
import bodyParser from "body-parser";
import mqtt from "mqtt";
import cors from "cors";

const app = express();

app.use(bodyParser.json());
app.use(cors());

const db = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "",
  database: "vehicle_data",
});

db.connect((err) => {
  if (err) {
    throw err;
  }
  console.log("MySQL connected");
});

// MQTT client
const mqttClient = mqtt.connect("mqtt://localhost:1883");

mqttClient.on("connect", () => {
  console.log("Connected to MQTT broker");
  mqttClient.subscribe("vehicle/interactions", (err) => {
    if (!err) {
      console.log("Subscribed to vehicle/interactions");
    }
  });
});

let goingDown = 0;
let goingUp = 0;
let billboardName = "BillboardA"; // Ganti sesuai dengan nama billboard yang sesuai

mqttClient.on("message", (topic, message) => {
  if (topic === "vehicle/interactions") {
    const data = JSON.parse(message.toString());
    goingDown = data.going_down;
    goingUp = data.going_up;
  }
});

const saveToDatabase = () => {
  const query =
    "INSERT INTO interactions (going_down, going_up, billboard_name) VALUES (?, ?, ?)";
    console.log("Saving data to database:", goingDown, goingUp, billboardName);
  db.query(query, [goingDown, goingUp, billboardName], (err) => {
    if (err) {
      console.error("Error saving data to database:", err);
    } else {
      console.log("Data saved to database");
    }
  });
};

// Save data every hour
// setInterval(saveToDatabase, 3600000);
// Save data every 2 minutes
setInterval(saveToDatabase, 120000);

app.get("/interactions", (req, res) => {
  const query = "SELECT * FROM interactions ORDER BY id DESC LIMIT 1";
  db.query(query, (err, result) => {
    if (err) {
      res.status(500).send(err);
    } else {
      res.send(result[0]);
    }
  });
});

app.get("/interactions/:billboardName", (req, res) => {
  const { billboardName } = req.params;
  const query =
    "SELECT timestamp, going_down as interactions FROM interactions WHERE billboard_name = ?";
  db.query(query, [billboardName], (err, results) => {
    if (err) {
      res.status(500).send(err);
    } else {
      res.send(results);
    }
  });
});

app.listen(3000, () => {
  console.log("Server started on port 3000");
});
