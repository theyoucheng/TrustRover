import os
import sys

import math
## Need Python version > 2.7
from collections import Counter
import cv2
import numpy as np

from darkflow.net.build import TFNet

options = {"model": "./cfg/yolo.cfg", "load": "./cfg/bin/yolo.weights", "threshold": 0.3}
tfnet = TFNet(options)


imgcv = cv2.imread("./routes/ormeau_road/(step3)54.5876023,-5.9239714.jpeg")
## let's predict
results = tfnet.return_predict(imgcv)

def decide_box_colour(str):
    colour_list=[{"label":"person","colour":(255,0,0)},{"label":"bicycle","colour":(0,255,0)},{"label":"car","colour":(0,0,255)},
                {"label":"bus","colour":(242,198,90)},{"label":"truck","colour":(144,75,154)},{"label":"motorbike","colour":(237,155,16)},
                {"label":"traffic light", "colour":(255,255,0)}]
    for obj in colour_list:
        if str==obj["label"]: colour = obj["colour"]


    #colour = (0,255,0)
    if str.startswith("danger"):
        colour = (0,0,255)
    return colour

def new_write_boundingboxes(results, imgcv, new_img):
    cv2.imwrite(new_img, imgcv)
    imgcv = cv2.imread(new_img)
    ## ROI: region of interest
    vtx = np.array([[0,0],[0,0],[0,0],[0,0]], np.int32)
    cv2.polylines(imgcv, [vtx], True, (0,255,255), 2)
    for result in results:
        if result['label']=='': continue
        cv2.rectangle(imgcv,
                     (result["topleft"]["x"], result["topleft"]["y"]),
                     (result["bottomright"]["x"],result["bottomright"]["y"]),
                     decide_box_colour(result["label"]), 2)
        text_x, text_y = int(result["topleft"]["x"]) - 10, int(result["topleft"]["y"]) - 10
        cv2.putText(imgcv, result["label"], (text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, decide_box_colour(result["label"]), 2, cv2.LINE_AA)
    cv2.imwrite(new_img, imgcv)

new_write_boundingboxes(results, imgcv, './predictions/result[6].png')







print(results)
