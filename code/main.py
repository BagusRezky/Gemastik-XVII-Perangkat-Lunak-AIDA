# import cv2
# import pandas as pd
# from imutils.video import FPS
# from ultralytics import YOLO
# from tracker import Tracker
# import argparse
# import time
# import subprocess
# import paho.mqtt.client as mqtt
# import json
# import numpy as np
# import sys

# def load_model(path):
#     return YOLO(path)

# def read_labels(path):
#     with open(path, 'r') as file:
#         labels_list = file.read().strip().split('\n')
#     return labels_list

# def get_detections(frame, model, labels):
#     results = model.predict(frame)
#     res = results[0].boxes.data
#     boxes = pd.DataFrame(res).astype('float')
#     detections = []

#     for _, row in boxes.iterrows():
#         x1, y1, x2, y2 = map(int, row[:4])
#         d = int(row[5])

#         if d < len(labels):
#             label = labels[d]
#             if 'car' in label:
#                 detections.append([x1, y1, x2, y2])
#         else:
#             print(f"Warning: Index {d} out of range for labels")

#     return detections

# def process_bboxes(bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1):
#     for bbox in bbox_id:
#         x3, y3, x4, y4, obj_id = bbox
#         cx = int((x3 + x4) // 2)
#         cy = int((y3 + y4) // 2)

#         process_downward_movement(cy, cy1, cy2, offset, obj_id, vh_down, counter, frame, cx)
#         process_upward_movement(cy, cy1, cy2, offset, obj_id, vh_up, counter1, frame, cx)

# def process_downward_movement(cy, cy1, cy2, offset, obj_id, vh_down, counter, frame, cx):
#     if cy1 - offset < cy < cy1 + offset:
#         vh_down[obj_id] = cy
#     if obj_id in vh_down and cy2 - offset < cy < cy2 + offset:
#         mark_object(frame, cx, cy, obj_id)
#         if obj_id not in counter:
#             counter.append(obj_id)

# def process_upward_movement(cy, cy1, cy2, offset, obj_id, vh_up, counter1, frame, cx):
#     if cy2 - offset < cy < cy2 + offset:
#         vh_up[obj_id] = cy
#     if obj_id in vh_up and cy1 - offset < cy < cy1 + offset:
#         mark_object(frame, cx, cy, obj_id)
#         if obj_id not in counter1:
#             counter1.append(obj_id)

# def mark_object(frame, cx, cy, obj_id):
#     cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
#     cv2.putText(frame, str(obj_id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

# def draw_lines(frame, cy1, cy2):
#     cv2.line(frame, (259, cy1), (811, cy1), (255, 255, 255), 1)
#     cv2.putText(frame, 'Line 1', (274, 318), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
#     cv2.line(frame, (154, cy2), (913, cy2), (255, 255, 255), 1)
#     cv2.putText(frame, 'Line 2', (154, 365), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

# def draw_counters(frame, counter, counter1):
#     d = len(counter)
#     cv2.putText(frame, f'Going Down: {d}', (60, 40), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
#     u = len(counter1)
#     cv2.putText(frame, f'Going Up: {u}', (60, 80), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

# def draw_fps(frame, num_frames, elapsed_time):
#     fps = num_frames / elapsed_time if elapsed_time > 0 else 0
#     txt_fps = f"FPS: {fps:.2f}"
#     cv2.putText(frame, txt_fps, (60, 120), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

# def on_connect(client, userdata, flags, rc):
#     print(f"Connected with result code {rc}")

# def publish_interactions(client, interactions):
#     topic = "vehicle/interactions"
#     message = json.dumps(interactions)
#     client.publish(topic, message)
#     print(f"Published interactions: {message}")

# def main(video_source, model_path, labels_path):
#     tracker = Tracker()
#     count = 0
#     cy1, cy2, offset = 323, 367, 6

#     vh_down, counter = {}, []
#     vh_up, counter1 = {}, []

#     cap = cv2.VideoCapture(video_source)
#     fps = FPS().start()  # Start the FPS counter
#     start_time = time.time()  # Start the timer
#     num_frames = 0  # Initialize the frame count

#     model = load_model(model_path)
#     labels = read_labels(labels_path)

#     mqtt_client = mqtt.Client()
#     mqtt_client.on_connect = on_connect
#     mqtt_client.connect("localhost", 1883, 60)
#     mqtt_client.loop_start()

#     # Open a file to write raw frames for debugging
#     with open('output.raw', 'wb') as f:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             count += 1
#             if count % 3 != 0:
#                 continue

#             frame = cv2.resize(frame, (1016, 488))

#             detections = get_detections(frame, model, labels)
#             bbox_id = tracker.update(detections)

#             process_bboxes(bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1)

#             draw_lines(frame, cy1, cy2)
#             draw_counters(frame, counter, counter1)

#             num_frames += 1
#             elapsed_time = time.time() - start_time  # Calculate elapsed time
#             draw_fps(frame, num_frames, elapsed_time)  # Draw FPS on the frame

#             try:
#                 frame_bytes = frame.tobytes()
#                 f.write(frame_bytes)  # Write frame to file
#                 sys.stdout.buffer.write(frame_bytes)
#                 sys.stdout.flush()
#                 print("Streaming frame to stdout")
#             except BrokenPipeError:
#                 print("Broken pipe error")
#                 break
#             except ValueError as e:
#                 print(f"ValueError: {e}")
#                 break

#             interactions = {"down": len(counter), "up": len(counter1)}
#             publish_interactions(mqtt_client, interactions)
#             print(f"Published interactions: {interactions}")

#     fps.stop()  # Stop the FPS counter when the loop exits
#     cap.release()
#     cv2.destroyAllWindows()
#     mqtt_client.loop_stop()

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--video', type=str, required=True)
#     parser.add_argument('--model', type=str, required=True)
#     parser.add_argument('--label', type=str, required=True)

#     args = parser.parse_args()

#     main(args.video, args.model, args.label)



import cv2
import pandas as pd
from imutils.video import FPS
from ultralytics import YOLO
from tracker import Tracker
import argparse
import time
import paho.mqtt.client as mqtt
import subprocess
import sys

# MQTT settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "vehicle/interactions"

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

def load_model(path):
    return YOLO(path)

def read_labels(path):
    with open(path, 'r') as file:
        labels_list = file.read().strip().split('\n')
    return labels_list

def get_detections(frame, model, labels):
    results = model.predict(frame)
    res = results[0].boxes.data
    boxes = pd.DataFrame(res).astype('float')
    detections = []

    for _, row in boxes.iterrows():
        x1, y1, x2, y2 = map(int, row[:4])
        d = int(row[5])
        label = labels[d]

        if 'car' in label:
            detections.append([x1, y1, x2, y2])

    return detections

def process_bboxes(bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1):
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

def draw_lines(frame, cy1, cy2):
    cv2.line(frame, (259, cy1), (811, cy1), (255, 255, 255), 1)
    cv2.putText(frame, 'Line 1', (274, 318), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
    cv2.line(frame, (154, cy2), (913, cy2), (255, 255, 255), 1)
    cv2.putText(frame, 'Line 2', (154, 365), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

def draw_counters(frame, counter, counter1):
    d = len(counter)
    cv2.putText(frame, f'Going Down: {d}', (60, 40), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
    u = len(counter1)
    cv2.putText(frame, f'Going Up: {u}', (60, 80), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

    # Publish counters to MQTT broker
    mqtt_client.publish(MQTT_TOPIC, f'{{"going_down": {d}, "going_up": {u}}}')

def draw_fps(frame, num_frames, elapsed_time):
    fps = num_frames / elapsed_time if elapsed_time > 0 else 0
    txt_fps = f"FPS: {fps:.2f}"
    cv2.putText(frame, txt_fps, (60, 120), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

def main(video_source, model_path, labels_path, rtmp_url):
    tracker = Tracker()
    count = 0
    cy1, cy2, offset = 323, 367, 6

    vh_down, counter = {}, []
    vh_up, counter1 = {}, []

    cap = cv2.VideoCapture(video_source)
    fps = FPS().start()  # Start the FPS counter
    start_time = time.time()  # Start the timer
    num_frames = 0  # Initialize the frame count

    model = load_model(model_path)
    labels = read_labels(labels_path)

    # Start FFmpeg process
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', '1020x500',  # Frame size
        '-r', '30',  # Frame rate
        '-i', '-',  # Input from stdin
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-f', 'flv',
        rtmp_url
    ]
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        count += 1
        if count % 3 != 0:
            continue

        frame = cv2.resize(frame, (1020, 500))

        detections = get_detections(frame, model, labels)
        bbox_id = tracker.update(detections)

        process_bboxes(bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1)

        draw_lines(frame, cy1, cy2)
        draw_counters(frame, counter, counter1)

        num_frames += 1
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        draw_fps(frame, num_frames, elapsed_time)  # Draw FPS on the frame

        # Write frame to FFmpeg process
        ffmpeg_process.stdin.write(frame.tobytes())

        cv2.imshow('Object Counter Program', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    fps.stop()  # Stop the FPS counter when the loop exits
    cap.release()
    cv2.destroyAllWindows()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', type=str, required=True)
    parser.add_argument('--model', type=str, required=True)
    parser.add_argument('--label', type=str, required=True)
    parser.add_argument('--rtmp_url', type=str, required=True, help="RTMP URL for streaming")

    args = parser.parse_args()

    print(f"Video: {args.video}")
    print(f"Model: {args.model}")
    print(f"Label: {args.label}")
    print(f"RTMP URL: {args.rtmp_url}")

    main(args.video, args.model, args.label, args.rtmp_url)

