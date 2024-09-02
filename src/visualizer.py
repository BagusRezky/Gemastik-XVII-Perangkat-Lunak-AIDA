import cv2
from logger import setup_logger

class Visualizer:
    def __init__(self):
        self.logger = setup_logger()

    def draw_lines(self, frame, cy1, cy2):
        cv2.line(frame, (259, cy1), (811, cy1), (255, 255, 255), 1)
        cv2.putText(frame, 'Line 1', (274, 318), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
        cv2.line(frame, (154, cy2), (913, cy2), (255, 255, 255), 1)
        cv2.putText(frame, 'Line 2', (154, 365), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
        self.logger.debug("Lines drawn on the frame.")

    def draw_counters(self, frame, counter, counter1):
        d = len(counter)
        u = len(counter1)
        self.logger.debug(f"Counters drawn: Going Down={d}, Going Up={u}")

    def draw_fps(self, frame, num_frames, elapsed_time):
        fps = num_frames / elapsed_time if elapsed_time > 0 else 0
        txt_fps = f"FPS: {fps:.2f}"
        cv2.putText(frame, txt_fps, (60, 120), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
        self.logger.debug(f"FPS drawn: {fps:.2f}")
