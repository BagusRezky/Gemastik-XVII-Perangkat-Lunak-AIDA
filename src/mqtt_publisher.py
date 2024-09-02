import paho.mqtt.client as mqtt
import json
from logger import setup_logger

class MQTTPublisher:
    def __init__(self):
        self.broker = "103.245.38.40"
        self.port = 1883
        self.topic = "vehicle/interactions"
        self.client = mqtt.Client()
        self.logger = setup_logger()
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")

    def publish_data(self, going_down, going_up):
        data = {
            "going_down": going_down,
            "going_up": going_up
        }
        try:
            self.client.publish(self.topic, json.dumps(data))
            self.logger.info(f"Published data to MQTT: {data}")
        except Exception as e:
            self.logger.error(f"Failed to publish data to MQTT: {e}")
