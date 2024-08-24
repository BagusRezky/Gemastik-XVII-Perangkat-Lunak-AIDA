import mqtt from "mqtt";

const mqttClient = mqtt.connect("mqtt://localhost:1883");

export default mqttClient;
