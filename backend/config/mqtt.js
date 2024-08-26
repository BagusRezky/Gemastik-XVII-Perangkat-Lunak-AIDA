import mqtt from "mqtt";

const mqttClient = mqtt.connect("mqtt://103.245.38.40:1883");

export default mqttClient;
