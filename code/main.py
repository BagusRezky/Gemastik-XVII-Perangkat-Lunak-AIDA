import cv2
import pandas as pd
from imutils.video import FPS
from ultralytics import YOLO
from tracker import Tracker
import argparse


def load_model(path):
    model = YOLO(path)

    return model

def read_labels(path):
    file = open(path, 'r')
    labels = file.read()
    labels_list = labels.split('\n')

    return labels_list

def main(video_source, model_path, labels_path):
    tracker = Tracker()
    count = 0
    cy1=323
    cy2=367
    offset=6

    vh_down={}
    counter=[]

    vh_up={}
    counter1=[]

    cap = cv2.VideoCapture(video_source)

    while True:
        ret, frame = cap.read()
        fps = FPS().start()

        if not ret:
            break

        count += 1

        if count % 3 != 0:
            continue

        frame = cv2.resize(frame,(1020,500))

        results = load_model(model_path).predict(frame)

        fps.update()
        fps.stop()

        res = results[0].boxes.data
        boxes = pd.DataFrame(res).astype('float')
        list = []

        labels = read_labels(labels_path)

        for index, row in boxes.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = labels[d]

            if 'car' in c:
                list.append(
                    [x1,y1,x2,y2]
                )
        
        bbox_id=tracker.update(list)

        for bbox in bbox_id:
            x3,y3,x4,y4,id=bbox
            cx = int(x3+x4)//2
            cy = int(y3+y4)//2

            # Going Down
            if cy1<(cy+offset) and cy1>(cy-offset):
                vh_down[id]=cy
            if id in vh_down:
                if cy2<(cy+offset) and cy2>(cy-offset):
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
                    if counter.count(id)==0:
                        counter.append(id)
            
            # Going Up
            if cy2<(cy+offset) and cy2>(cy-offset):
                vh_up[id]=cy
            if id in vh_up:
                if cy1<(cy+offset) and cy1>(cy-offset):
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
                    if counter1.count(id)==0:
                        counter1.append(id)
    
        cv2.line(frame,(259,cy1),(811,cy1),(255,255,255),1)
        cv2.putText(frame,('1line'),(274,318),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

        cv2.line(frame,(154,cy2),(913,cy2),(255,255,255),1)
        cv2.putText(frame,('2line'),(154,365),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
        d=(len(counter))
        cv2.putText(frame,('goingdown: -')+str(d),(60,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
        u=(len(counter1))
        cv2.putText(frame,('goingup: -')+str(u),(60,130),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
        
        txt_fps = "FPS: {:.2f}".format(fps.fps())
        cv2.putText(frame, txt_fps,(60,180),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
        
        print(counter)

        cv2.imshow('Counter', frame)
        if cv2.waitKey(1)&0xFF==ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', type=str, required=True)
    parser.add_argument('--model', type=str, required=True)
    parser.add_argument('--label', type=str, required=True)

    args = parser.parse_args()

    main(args.video, args.model, args.label)