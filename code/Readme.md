# How to Run

`$ python main.py --video 'path_to_video' --model 'path_to_model' --label 'path_to_label'`

Example:

`$ python main.py --video 'veh2.mp4' --model 'yolov8m' --label 'coco.txt'`

## Running with OpenVino Model

We already convert the `yolov8m.pt` model into OpenVino model with int8 data format for faster inference process. To run the `main.py` using OpenVino model,

`$ python main.py --video 'veh2.mp4' --model 'yolov8m_int8_openvino_model' --label 'coco.txt'`