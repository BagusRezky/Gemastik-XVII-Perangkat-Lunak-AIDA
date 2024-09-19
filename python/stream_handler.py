import cv2
import time 
import threading

class VideoStreamHandler:
    def __init__(self, source):
        self.source = source
        self.cap = cv2.VideoCapture(self.source)
        self.ret = False
        self.frame = None
        self.running = True
        self.lock = threading.Lock()

        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while self.running:
            with self.lock:
                self.ret, self.frame = self.cap.read()
                if not self.ret:
                    self.reconnect()

    def reconnect(self):
        self.cap.release()
        time.sleep(2)
        self.cap = cv2.VideoCapture(self.source)

    def read(self):
        with self.lock:
            return self.ret, self.frame

    def release(self):
        self.running = False
        self.thread.join()
        self.cap.release()