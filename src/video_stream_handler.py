import cv2
import threading
from logger import setup_logger

class VideoStreamHandler:
    def __init__(self, source):
        self.logger = setup_logger()
        self.logger.info("Initializing video stream...")
        
        self.cap = cv2.VideoCapture(source)

        # Set frame width and height to 640x480
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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
        self.logger.info("Video stream released.")