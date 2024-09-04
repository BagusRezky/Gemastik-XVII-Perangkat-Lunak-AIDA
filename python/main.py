import cv2
import pandas as pd
from imutils.video import FPS
from ultralytics import YOLO
from tracker import Tracker
import json
import argparse
import time
import paho.mqtt.client as mqtt
import subprocess
import sys
import threading
import logging
import os
import torch 

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Determine the number of the run
run_number = 1
while os.path.exists(f'logs/run_{run_number}.log'):
    run_number += 1

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/run_{run_number}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Device: {device}")

# MQTT settings
MQTT_BROKER = "103.245.38.40"
MQTT_PORT = 1883
MQTT_TOPIC = "vehicle/interactions"

# Initialize MQTT client
mqtt_client = mqtt.Client()
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
except Exception as e:
    logger.error(f"Failed to connect to MQTT broker: {e}")
    sys.exit(1)

class VideoStreamHandler:
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.ret = False
        self.frame = None
        self.running = True
        self.lock = threading.Lock()

        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame

    def release(self):
        self.running = False
        self.thread.join()
        self.cap.release()
        logger.info("Video stream released.")

def load_model(path):
    logger.info(f"Loading model from {path}")
    return YOLO(path)

def read_labels(path):
    try:
        with open(path, 'r') as file:
            labels_list = file.read().strip().split('\n')
        logger.info(f"Labels loaded: {labels_list}")
        return labels_list
    except Exception as e:
        logger.error(f"Error reading labels from {path}: {e}")
        return []

def get_detections(frame, model, labels):
    logger.debug("Getting detections from the frame.")
    try:
        results = model.predict(frame)
        res = results[0].boxes.data
        boxes = pd.DataFrame(res).astype('float')
        detections = []

        for _, row in boxes.iterrows():
            x1, y1, x2, y2 = map(int, row[:4])
            d = int(row[5])
            if d >= len(labels):
                logger.warning(f"Label index out of range: {d}")
                continue
            label = labels[d]
            if 'car' in label:
                detections.append([x1, y1, x2, y2])

        return detections
    except Exception as e:
        logger.error(f"Error during detection: {e}")
        return []

def process_bboxes(bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1):
    logger.debug("Processing bounding boxes.")
    for bbox in bbox_id:
        x3, y3, x4, y4, obj_id = bbox
        cx = int((x3 + x4) // 2)
        cy = int((y3 + y4) // 2)

        process_downward_movement(cy, cy1, cy2, offset, obj_id, vh_down, counter, frame, cx)
        process_upward_movement(cy, cy1, cy2, offset, obj_id, vh_up, counter1, frame, cx)

def process_downward_movement(cy, cy1, cy2, offset, obj_id, vh_down, counter, frame, cx):
    if cy1 - offset < cy < cy1 + offset:
        vh_down[obj_id] = cy
    if obj_id in vh_down and cy2 - offset < cy < cy2 + offset:
        mark_object(frame, cx, cy, obj_id)
        if obj_id not in counter:
            counter.append(obj_id)

def process_upward_movement(cy, cy1, cy2, offset, obj_id, vh_up, counter1, frame, cx):
    if cy2 - offset < cy < cy2 + offset:
        vh_up[obj_id] = cy
    if obj_id in vh_up and cy1 - offset < cy < cy1 + offset:
        mark_object(frame, cx, cy, obj_id)
        if obj_id not in counter1:
            counter1.append(obj_id)

def mark_object(frame, cx, cy, obj_id):
    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
    cv2.putText(frame, str(obj_id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
    logger.debug(f"Marked object {obj_id} at ({cx}, {cy})")

def draw_lines(frame, cy1, cy2):
    cv2.line(frame, (259, cy1), (811, cy1), (255, 255, 255), 1)
    cv2.putText(frame, 'Line 1', (274, 318), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
    cv2.line(frame, (154, cy2), (913, cy2), (255, 255, 255), 1)
    cv2.putText(frame, 'Line 2', (154, 365), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
    logger.debug("Lines drawn on the frame.")

def publish_data(going_down, going_up):
    data = {
        "going_down": going_down,
        "going_up": going_up
    }
    try:
        mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
        logger.info(f"Published data to MQTT: {data}")
    except Exception as e:
        logger.error(f"Failed to publish data to MQTT: {e}")

def draw_counters(frame, counter, counter1):
    d = len(counter)
    u = len(counter1)
    publish_data(d, u)
    logger.debug(f"Counters drawn: Going Down={d}, Going Up={u}")

def draw_fps(frame, num_frames, elapsed_time):
    fps = num_frames / elapsed_time if elapsed_time > 0 else 0
    txt_fps = f"FPS: {fps:.2f}"
    cv2.putText(frame, txt_fps, (60, 120), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
    logger.debug(f"FPS drawn: {fps:.2f}")

def main(model_path, labels_path, rtmp_url):
    logger.info("Starting main function.")
    try:
        tracker = Tracker()
        count = 0
        cy1, cy2, offset = 323, 367, 6

        vh_down, counter = {}, []
        vh_up, counter1 = {}, []

        # stream_handler = VideoStreamHandler('rtsp://admin:CRPBEB@192.168.88.229')
        stream_handler = VideoStreamHandler('./veh2.mp4')

        fps = FPS().start()
        start_time = time.time()
        num_frames = 0

        model = load_model(model_path)
        labels = read_labels(labels_path)

        # Start FFmpeg process
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', '704x576',
            '-r', '10',
            '-i', '-',
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-maxrate', '1500k',
            '-bufsize', '3000k',
            '-pix_fmt', 'yuv420p',
            '-g', '50',
            '-f', 'flv',
            rtmp_url
        ]
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

        logger.info("FFmpeg process started.")

        while True:
            ret, frame = stream_handler.read()
            if not ret or frame is None:
                logger.warning("Failed to retrieve frame from stream.")
                continue

            count += 1
            if count % 3 != 0:
                continue

            frame = cv2.resize(frame, (704, 576))

            detections = get_detections(frame, model, labels)
            bbox_id = tracker.update(detections)

            process_bboxes(bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1)

            draw_lines(frame, cy1, cy2)
            draw_counters(frame, counter, counter1)

            num_frames += 1
            elapsed_time = time.time() - start_time
            draw_fps(frame, num_frames, elapsed_time)

            if ffmpeg_process.stdin:
                try:
                    ffmpeg_process.stdin.write(frame.tobytes())
                except BrokenPipeError:
                    logger.error("FFmpeg process broke. Restarting...")
                    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

            fps.update()
            cv2.imshow('Object Counter Program', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        fps.stop()
        logger.info(f"[INFO] Elapsed time: {fps.elapsed():.2f}")
        logger.info(f"[INFO] Approx. FPS: {fps.fps():.2f}")

    except Exception as e:
        logger.error(f"Exception in main function: {e}")

    finally:
        stream_handler.release()
        cv2.destroyAllWindows()
        if ffmpeg_process.stdin:
            ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        logger.info("Application closed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Object detection and counting.')
    parser.add_argument('--model', default='./yolov3-tinyu.pt', help='Model path')
    parser.add_argument('--labels', default='../coco.txt', help='Labels path')
    parser.add_argument('--rtmp', default='rtmp://103.245.38.40/live/test', help='RTMP URL')
    args = parser.parse_args()

    main(args.model, args.labels, args.rtmp)
