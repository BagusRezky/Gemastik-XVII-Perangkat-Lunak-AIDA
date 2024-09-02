import cv2
import pandas as pd
from ultralytics import YOLO
import torch
from logger import setup_logger

class ObjectDetector:
    def __init__(self, model_path, labels_path):
        self.model = self.load_model(model_path)
        self.labels = self.read_labels(labels_path)
        self.logger = setup_logger()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger.info(f"Device: {self.device}")

    def load_model(self, path):
        self.logger.info(f"Loading model from {path}")
        model = YOLO(path)
        model.to(self.device)  # Move model to the appropriate device (CPU or CUDA)
        return model

    def read_labels(self, path):
        try:
            with open(path, 'r') as file:
                labels_list = file.read().strip().split('\n')
            self.logger.info(f"Labels loaded: {labels_list}")
            return labels_list
        except Exception as e:
            self.logger.error(f"Error reading labels from {path}: {e}")
            return []

    def get_detections(self, frame):
        self.logger.debug("Getting detections from the frame.")
        try:
            results = self.model.predict(frame)
            res = results[0].boxes.data
            boxes = pd.DataFrame(res).astype('float')
            detections = []

            for _, row in boxes.iterrows():
                x1, y1, x2, y2 = map(int, row[:4])
                d = int(row[5])
                if d >= len(self.labels):
                    self.logger.warning(f"Label index out of range: {d}")
                    continue
                label = self.labels[d]
                if 'car' in label:
                    detections.append([x1, y1, x2, y2])

            return detections
        except Exception as e:
            self.logger.error(f"Error during detection: {e}")
            return []

    def process_bboxes(self, bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1):
        self.logger.debug("Processing bounding boxes.")
        for bbox in bbox_id:
            x3, y3, x4, y4, obj_id = bbox
            cx = int((x3 + x4) // 2)
            cy = int((y3 + y4) // 2)

            self.process_downward_movement(cy, cy1, cy2, offset, obj_id, vh_down, counter, frame, cx)
            self.process_upward_movement(cy, cy1, cy2, offset, obj_id, vh_up, counter1, frame, cx)

    def process_downward_movement(self, cy, cy1, cy2, offset, obj_id, vh_down, counter, frame, cx):
        if cy1 - offset < cy < cy1 + offset:
            vh_down[obj_id] = cy
        if obj_id in vh_down and cy2 - offset < cy < cy2 + offset:
            self.mark_object(frame, cx, cy, obj_id)
            if obj_id not in counter:
                counter.append(obj_id)

    def process_upward_movement(self, cy, cy1, cy2, offset, obj_id, vh_up, counter1, frame, cx):
        if cy2 - offset < cy < cy2 + offset:
            vh_up[obj_id] = cy
        if obj_id in vh_up and cy1 - offset < cy < cy1 + offset:
            self.mark_object(frame, cx, cy, obj_id)
            if obj_id not in counter1:
                counter1.append(obj_id)

    def mark_object(self, frame, cx, cy, obj_id):
        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
        cv2.putText(frame, str(obj_id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
        self.logger.debug(f"Marked object {obj_id} at ({cx},{cy})")
