from imutils.video import FPS

class FPSTracker:
    def __init__(self):
        self.fps = FPS()

    def start(self):
        self.fps.start()

    def update(self):
        self.fps.update()

    def stop(self):
        self.fps.stop()

    def elapsed(self):
        return self.fps.elapsed()

    def fps(self):
        return self.fps.fps()
