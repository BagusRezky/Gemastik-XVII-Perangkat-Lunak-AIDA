# Vehicle Object Detection for Billboard Advertisements

This project focuses on detecting passerby individuals in a video using the YOLOv8 object detection model. It provides instructions on how to run the detection with both the original YOLOv8 model and an optimized version using the OpenVINO toolkit.

### Run the code

1. Clone the repo :

   `$ git clone https://github.com/BagusRezky/ObjectDetectionwithYolov8.git`
2. Install the required dependencies :

   `$ pip install -r requirements.txt`
3. Execute the `main.py` script with the following command-line arguments:

   `$ python main.py --video 'path_to_video' --model 'path_to_model' --label 'path_to_label'`

### Example

`$ python main.py --video 'veh2.mp4' --model 'yolov8m' --label 'coco.txt'`

* Replace `'path_to_video'` with the path to the input video file.
* Replace `'path_to_model'` with the path to the YOLOv8 model (`yolov8m.pt` in the original form or `yolov8m_int8_openvino_model` if using the OpenVINO-converted model).
* Replace `'path_to_label'` with the path to the file containing the labels (e.g., `coco.txt`).

### Running with OpenVino Model

We already convert the `yolov8m.pt` model into OpenVino model with int8 data format for faster inference process. To run the `main.py` using OpenVino model,

`$ python main.py --video 'veh2.mp4' --model 'yolov8m_int8_openvino_model' --label 'coco.txt'`

### Additional Notes

* Ensure Python is installed on your system.
* Make sure to install necessary libraries and frameworks such as OpenCV, PyTorch (for the original YOLOv8 model), and OpenVINO if using the converted model.
* Using a virtual environment is suggested.
* Ensure that the model files (`yolov8m.pt`, `yolov8m_int8_openvino_model`), and label file (`coco.txt`) are present in the specified locations.
