from ultralytics import YOLO

model = YOLO('yolov8m.pt')
model.export(format='openvino', imgsz=640, int8=True)