import argparse
import cv2
import time
import subprocess

from video_stream_handler import VideoStreamHandler
from object_detector import ObjectDetector
from mqtt_publisher import MQTTPublisher
from fps_tracker import FPSTracker
from visualizer import Visualizer
from logger import setup_logger
from tracker import Tracker

def main(model_path, labels_path, rtmp_url):
    logger = setup_logger()
    tracker = Tracker()
    count = 0
    cy1, cy2, offset = 323, 367, 20

    vh_down, counter = {}, []
    vh_up, counter1 = {}, []

    # stream_handler = VideoStreamHandler('rtsp://admin:CRPBEB@192.168.88.229')
    stream_handler = VideoStreamHandler('./veh2.mp4')

    fps_tracker = FPSTracker()
    fps_tracker.start()
    start_time = time.time()
    num_frames = 0

    object_detector = ObjectDetector(model_path, labels_path)
    mqtt_publisher = MQTTPublisher()

    visualizer = Visualizer()

    # Add FFmpeg logging configuration
    ffmpeg_log_file = f'logs/ffmpeg_run_{logger.run_number}.log'

    # Update FFmpeg command to log to file
    ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', '640x480',
            '-r', '15',
            '-i', '-',
            '-g', '15',
            # '-c:v', 'h264_nvmpi',
            '-c:v', 'libx264',
            '-b:v', '300k',
            '-preset', 'ultrafast',
            '-maxrate', '300k',
            '-bufsize', '600k',
            '-pix_fmt', 'yuv420p',
            '-g', '50',
            '-f', 'flv',
            rtmp_url,
            '-loglevel', 'info',
            '-report',
        ]

    # Redirect FFmpeg output to log file
    with open(ffmpeg_log_file, 'w') as log_file:
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=log_file, stderr=subprocess.STDOUT)

    logger.info(f"FFmpeg process started with logging to {ffmpeg_log_file}.")

    while True:
        ret, frame = stream_handler.read()
        if not ret or frame is None:
            logger.warning("Failed to retrieve frame from stream.")
            continue

        count += 1
        if count % 3 != 0:
            continue

        frame = cv2.resize(frame, (640, 480))

        detections = object_detector.get_detections(frame)
        bbox_id = tracker.update(detections)

        object_detector.process_bboxes(bbox_id, frame, cy1, cy2, offset, vh_down, counter, vh_up, counter1)

        visualizer.draw_lines(frame, cy1, cy2)
        visualizer.draw_counters(frame, counter, counter1)

        num_frames += 1
        elapsed_time = time.time() - start_time
        visualizer.draw_fps(frame, num_frames, elapsed_time)

        mqtt_publisher.publish_data(len(counter), len(counter1))

        if ffmpeg_process.stdin:
            try:
                ffmpeg_process.stdin.write(frame.tobytes())
            except BrokenPipeError:
                logger.error("FFmpeg process broke. Restarting...")
                ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

        fps_tracker.update()
        cv2.imshow('Object Counter Program', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    fps_tracker.stop()
    logger.info(f"[INFO] Elapsed time: {fps_tracker.elapsed():.2f}")
    logger.info(f"[INFO] Approx. FPS: {fps_tracker.get_fps():.2f}")

    stream_handler.release()
    cv2.destroyAllWindows()
    if ffmpeg_process.stdin:
        ffmpeg_process.stdin.close()
    ffmpeg_process.wait()
    logger.info("Application closed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Object detection and counting.')
    parser.add_argument('--model', default='./best.pt', help='Model path')
    parser.add_argument('--labels', default='../coco.txt', help='Labels path')
    parser.add_argument('--rtmp', default='rtmp://103.245.38.40/live/test', help='RTMP URL')
    args = parser.parse_args()

    main(args.model, args.labels, args.rtmp)
