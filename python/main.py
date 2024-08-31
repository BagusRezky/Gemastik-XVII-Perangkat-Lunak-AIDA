import cv2
import pandas as pd
from imutils.video import FPS
from ultralytics import YOLO
from tracker import Tracker
import json
import argparse
import time
import subprocess
import sys
import torch
import threading
import logging
import paho.mqtt.client as mqtt

# Setting up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("./log/app.log"),
                              logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)

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

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {device}")

# class VideoCaptureThread:
#     def __init__(self, src):
#         self.cap = cv2.VideoCapture(src)
#         if not self.cap.isOpened():
#             raise ValueError(f"Unable to open video source {src}")
#         self.frame = None
#         self.lock = threading.Lock()
#         self.stopped = False

#         thread = threading.Thread(target=self.update, args=())
#         thread.daemon = True
#         thread.start()
#         logger.info("VideoCaptureThread started.")

#     def update(self):
#         while not self.stopped:
#             ret, frame = self.cap.read()
#             if not ret:
#                 logger.warning("Frame capture failed. Stopping video capture.")
#                 self.stop()
#                 break
#             with self.lock:
#                 self.frame = frame

#     def read(self):
#         with self.lock:
#             return self.frame.copy() if self.frame is not None else None

#     def stop(self):
#         self.stopped = True
#         if self.cap.isOpened():
#             self.cap.release()
#         logger.info("VideoCaptureThread stopped.")

def load_model(path):
    logger.info(f"Loading model from {path}")
    model = YOLO(path)
    model.to(device)
    logger.info("Model loaded successfully")
    return model

def read_labels(path):
    logger.info(f"Reading labels from {path}")
    with open(path, 'r') as file:
        labels_list = file.read().strip().split('\n')
    logger.info(f"Labels loaded: {labels_list}")
    return labels_list

def get_detections(frame, model, labels):
    results = model(frame)
    detections = []

    valid_classes = {'person', 'car', 'motorcycle', 'bus', 'truck'}

    for result in results:
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            confidence = box.conf[0]
            class_id = int(box.cls[0])

            if class_id < len(labels):
                label = labels[class_id]
                if label in valid_classes:
                    detections.append([x1, y1, x2, y2, confidence, label])
            else:
                logger.warning(f"Invalid class index: {class_id}")

    logger.debug(f"Detected {len(detections)} valid objects")
    return detections

def process_bboxes(bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1):
    for bbox in bbox_id:
        if len(bbox) != 6:
            logger.warning(f"Unexpected bbox format: {bbox}")
            continue
        x3, y3, x4, y4, obj_id, label = bbox
        cx = int((x3 + x4) // 2)
        cy = int((y3 + y4) // 2)

        process_downward_movement(cy, cy1, cy2, offset, obj_id, vh_down, counter, frame, cx, label)
        process_upward_movement(cy, cy1, cy2, offset, obj_id, vh_up, counter1, frame, cx, label)

def process_downward_movement(cy, cy1, cy2, offset, obj_id, vh_down, counter, frame, cx, label):
    if cy1 - offset < cy < cy1 + offset:
        vh_down[obj_id] = cy
    if obj_id in vh_down and cy2 - offset < cy < cy2 + offset:
        mark_object(frame, cx, cy, obj_id, label)
        if obj_id not in counter:
            counter.append(obj_id)
            logger.info(f"{label.capitalize()} {obj_id} counted going down")

def process_upward_movement(cy, cy1, cy2, offset, obj_id, vh_up, counter1, frame, cx, label):
    if cy2 - offset < cy < cy2 + offset:
        vh_up[obj_id] = cy
    if obj_id in vh_up and cy1 - offset < cy < cy1 + offset:
        mark_object(frame, cx, cy, obj_id, label)
        if obj_id not in counter1:
            counter1.append(obj_id)
            logger.info(f"{label.capitalize()} {obj_id} counted going up")

def mark_object(frame, cx, cy, obj_id, label):
    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
    cv2.putText(frame, f"{label} {obj_id}", (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

def draw_lines(frame, cy1, cy2):
    cv2.line(frame, (259, cy1), (811, cy1), (255, 255, 255), 1)
    cv2.putText(frame, 'Line 1', (274, 318), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
    cv2.line(frame, (154, cy2), (913, cy2), (255, 255, 255), 1)
    cv2.putText(frame, 'Line 2', (154, 365), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

def publish_data(going_down, going_up):
    data = {
        "going_down": going_down,
        "going_up": going_up
    }
    try:
        mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
        logger.info(f"Published data: {data}")
    except Exception as e:
        logger.error(f"Failed to publish MQTT data: {e}")

def draw_counters(frame, counter, counter1):
    d = len(counter)
    u = len(counter1)
    publish_data(d, u)

def draw_fps(frame, num_frames, elapsed_time):
    fps = num_frames / elapsed_time if elapsed_time > 0 else 0
    txt_fps = f"FPS: {fps:.2f}"
    cv2.putText(frame, txt_fps, (60, 120), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
    logger.debug(f"Current FPS: {fps:.2f}")

def create_capture():
    logger.info("Attempting to connect to stream")
    try:
        cap = cv2.VideoCapture('rtsp://admin:CRPBEB@192.168.88.229')
        if not cap.isOpened():
            logger.error("Failed to open video stream")
            return None
        logger.info("Successfully connected to the stream")
        return cap
    except Exception as e:
        logger.error(f"Error creating video capture: {e}")
        return None

def reconnect_stream(max_retries=5, retry_interval=5):
    for attempt in range(max_retries):
        logger.info(f"Attempting to reconnect to stream (attempt {attempt + 1}/{max_retries})")
        cap = create_capture()
        if cap is not None:
            return cap
        logger.warning(f"Failed to connect. Retrying in {retry_interval} seconds...")
        time.sleep(retry_interval)
    logger.error("Max retries reached. Could not reconnect to the stream.")
    return None

def read_frame_with_timeout(cap, timeout=10):
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if ret:
            return ret, frame
        if time.time() - start_time > timeout:
            logger.warning("Frame read timed out")
            return False, None
        time.sleep(0.1)

def main(model_path, labels_path):
    logger.info("Starting main function")
    tracker = Tracker()
    count = 0
    cy1, cy2, offset = 323, 367, 6

    vh_down, counter = {}, []
    vh_up, counter1 = {}, []

    # cap = cv2.VideoCapture('./veh2.mp4')
    cap = cv2.VideoCapture('rtsp://admin:CRPBEB@192.168.88.229')

    if not cap.isOpened():
        logger.error("Failed to open video file")
        return
    logger.info("Video capture initialized")

    fps = FPS().start()
    start_time = time.time()
    num_frames = 0

    try:
        model = load_model(model_path)
        labels = read_labels(labels_path)
    except Exception as e:
        logger.error(f"Failed to load model or labels: {e}")
        return

    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', '704x576',
        '-r', '15',
        '-i', '-',
        '-an',
        '-g', '30',
        '-c:v', 'libx264', 
        '-b:v', '256k',
        '-maxrate', '256k',
        '-preset', 'veryfast',
        '-tune', 'zerolatency',
        '-profile:v', 'baseline',
        '-level', '3.0',
        # '-x264-params', 'nal-hrd=cbr:force-cfr=1',
        '-vf', 'format=yuv420p',
        # '-vcodec', 'libx264',
        '-f', 'tee',
        '-map', '0:v',
        '[f=flv]rtmp://103.245.38.40/live/test|[f=hls:hls_time=10:hls_list_size=0:hls_segment_filename=/mnt/hls/test%0.ts]/mnt/hls/test.m3u8'
    ]
    try:
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
        logger.info("FFmpeg process started")
    except Exception as e:
        logger.error(f"Failed to start FFmpeg process: {e}")
        return

    try:
        while True:
            ret, frame = read_frame_with_timeout(cap)
            if not ret:
                logger.warning("Failed to capture frame. Attempting to reconnect...")
                cap.release()
                cap = reconnect_stream()
                if cap is None:
                    logger.error("Failed to reconnect. Exiting.")
                    break
                continue

            count += 1
            if count % 3 != 0:
                continue

            frame = cv2.resize(frame, (704, 576))

            try:
                detections = get_detections(frame, model, labels)
                logger.debug(f"Detections: {detections}")
                
                bbox_id = tracker.update(detections)
                logger.debug(f"Tracker output: {bbox_id}")
                
                process_bboxes(bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1)
            except Exception as e:
                logger.error(f"Error in detection or tracking: {e}")
                continue

            draw_lines(frame, cy1, cy2)
            draw_counters(frame, counter, counter1)

            num_frames += 1
            elapsed_time = time.time() - start_time
            draw_fps(frame, num_frames, elapsed_time)

            ffmpeg_process.stdin.write(frame.tobytes())

            cv2.imshow('Object Counter Program', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("User requested to quit")
                break

    except Exception as e:
        logger.error(f"An error occurred during main loop: {e}")
    finally:
        fps.stop()
        logger.info(f"Elapsed time: {fps.elapsed():.2f}")
        logger.info(f"Approx. FPS: {fps.fps():.2f}")

        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        logger.info("Resources released and program finished")

        publish_data(len(counter), len(counter1))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, required=True)
    parser.add_argument('--label', type=str, required=True)

    args = parser.parse_args()

    logger.info(f"Starting program with model: {args.model}, label: {args.label}")
    main(args.model, args.label)