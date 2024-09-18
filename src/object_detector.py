import cv2
import pandas as pd
from ultralytics import YOLO
import torch
from logger import setup_logger

class ObjectDetector:
    def __init__(self, model_path, labels_path):
        # Initialize logger first
        self.logger = setup_logger()
        self.logger.info("Logger initialized successfully.")
        
        # Set device before loading the model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger.info(f"Device: {self.device}")
        
        # Now load the model and labels
        self.model = self.load_model(model_path)
        self.labels = self.read_labels(labels_path)

    def load_model(self, path):
        if not hasattr(self, 'logger'):
            raise AttributeError("Logger not initialized. Ensure logger is set up before calling this method.")
        self.logger.info(f"Loading model from {path}")
        model = YOLO(path)
        model.to(self.device)
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

    def get_detections(self, frame, conf_thresh=0.3):
        self.logger.debug("Getting detections from the frame.")
        try:
            results = self.model.predict(frame, conf=conf_thresh)
            res = results[0].boxes.data
            boxes = pd.DataFrame(res).astype('float')
            detections = []

            for _, row in boxes.iterrows():
                x1, y1, x2, y2 = map(int, row[:4])
                d = int(row[5])
                confidence = row[4]  # Assuming confidence score is in index 4
                if confidence < conf_thresh:
                    continue  # Skip low-confidence detections
                
                if d >= len(self.labels):
                    self.logger.warning(f"Label index out of range: {d}")
                    continue
                
                label = self.labels[d]
                if 'car' in label:  # Assuming you're looking for cars
                    detections.append([x1, y1, x2, y2])

            return detections
        except Exception as e:
            self.logger.error(f"Error during detection: {e}")
            return []

    def process_movement(self, cy, cy1, cy2, offset, obj_id, vh_dict, counter, frame, cx, direction):
        """
        Unified movement processing for both upward and downward movements.
        `direction`: should be 'up' or 'down'
        """
        if (cy1 - offset < cy < cy1 + offset) and direction == 'down':
            vh_dict[obj_id] = cy
        elif (cy2 - offset < cy < cy2 + offset) and direction == 'up':
            vh_dict[obj_id] = cy

        if obj_id in vh_dict and ((cy2 - offset < cy < cy2 + offset and direction == 'down') or
                                  (cy1 - offset < cy < cy1 + offset and direction == 'up')):
            self.mark_object(frame, cx, cy, obj_id)
            if obj_id not in counter:
                counter.append(obj_id)

    def process_bboxes(self, bbox_id, frame, cy1, cy2, offset, vh_down, counter_down, vh_up, counter_up):
        self.logger.debug("Processing bounding boxes.")
        for bbox in bbox_id:
            x3, y3, x4, y4, obj_id = bbox
            cx = int((x3 + x4) // 2)
            cy = int((y3 + y4) // 2)

            # Process both downward and upward movements in one function
            self.process_movement(cy, cy1, cy2, offset, obj_id, vh_down, counter_down, frame, cx, 'down')
            self.process_movement(cy, cy1, cy2, offset, obj_id, vh_up, counter_up, frame, cx, 'up')

    def mark_object(self, frame, cx, cy, obj_id):
        # Draw circle and text on the object
        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
        cv2.putText(frame, str(obj_id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
        self.logger.info(f"Marked object {obj_id} at ({cx},{cy})")
