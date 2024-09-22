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
      goingDown = data.going_down; // Update variabel, tidak diakumulasi
      goingUp = data.going_up;
    }
  });

  setInterval(() => {
    // Simpan data ke database
    dbService.saveToDatabase(goingDown, goingUp, billboardName);

    console.log(`Data saved: Going Down: ${goingDown}, Going Up: ${goingUp}`);

    // Reset variabel setelah menyimpan ke database
    goingDown = 0;
    goingUp = 0;
  }, 3600000); // Save data every hour
};

export default { init };
