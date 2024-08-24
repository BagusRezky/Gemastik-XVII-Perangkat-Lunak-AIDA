import mqttClient from "../../config/mqtt.js";
import dbService from "./dbService.js";

let goingDown = 0;
let goingUp = 0;
let billboardName = "BillboardA"; // Ganti sesuai dengan nama billboard yang sesuai

const init = () => {
  mqttClient.on("connect", () => {
    console.log("Connected to MQTT broker");
    mqttClient.subscribe("vehicle/interactions", (err) => {
      if (!err) {
        console.log("Subscribed to vehicle/interactions");
      }
    });
  });

  mqttClient.on("message", (topic, message) => {
    if (topic === "vehicle/interactions") {
      const data = JSON.parse(message.toString());
      goingDown = data.going_down;
      goingUp = data.going_up;
    }
  });

  setInterval(() => {
    dbService.saveToDatabase(goingDown, goingUp, billboardName);
    // Reset the data after 1 hour
    goingDown = 0;
    goingUp = 0;
  }, 3600000); // Save data every hour
};

export default { init };
