import os
import sys

import math
## Need Python version > 2.7
from collections import Counter
import cv2
import numpy as np
import imageio
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import json
from darkflow.net.build import TFNet
from car import car
from decision_maker import decision_maker


# options = {"model": "./cfg/yolo.cfg", "load": "./cfg/bin/yolo.weights", "threshold": 0.4, "gpu": 1.0}
# tfnet = TFNet(options)


# optionsv2 = {"model": "./cfg/yolov2.cfg", "load": "./cfg/bin/yolov2.weights", "threshold": 0.4, "gpu": 1.0}
# tfnetv2 = TFNet(optionsv2)

# optionstiny = {"model": "./cfg/yolov2.cfg", "load": "./cfg/bin/yolov2.weights", "threshold": 0.4, "gpu": 1.0}
# tfnettiny = TFNet(optionstiny)

path =  "./routes/europa/(step_4)54.5953108,-5.9346429.jpeg"
driving_path = np.array([[190,200],[100,400],[300,400],[210,200]], np.int32)
warning_left_sector = np.array([[driving_path[1][0],driving_path[0][1]],
                                [driving_path[1][0],driving_path[0][1]+50],
                                [driving_path[1][0]+60,driving_path[0][1]+50],
                                [driving_path[0][0],driving_path[0][1]]], np.int32)
danger_left_sector = np.array([[warning_left_sector[1][0],warning_left_sector[1][1]],
                                [0,300],
                                [0,400],
                                [driving_path[1][0],driving_path[1][1]],
                                [warning_left_sector[2][0],warning_left_sector[2][1]]], np.int32)
warning_right_sector = np.array([[driving_path[3][0],driving_path[3][1]],
                                [driving_path[3][0]+30,driving_path[3][1]+50],
                                [driving_path[2][0],driving_path[0][1]+50],
                                [driving_path[2][0],driving_path[3][1]]], np.int32)
danger_right_sector = np.array([[warning_right_sector[1][0],warning_right_sector[1][1]],
                                [driving_path[2][0],driving_path[2][1]],
                                [driving_path[2][0]+40,driving_path[2][1]],
                                [warning_right_sector[1][0]+40,warning_right_sector[1][1]]], np.int32)
stopping_zone = np.array([[driving_path[0][0]-30,driving_path[0][1]+100],
                                [driving_path[1][0]+20,driving_path[1][1]],
                                [driving_path[2][0]-20,driving_path[2][1]],
                                [driving_path[3][0]+30,driving_path[3][1]+100]], np.int32)
slow_zone = np.array([[driving_path[0][0],driving_path[0][1]+50],
                                [stopping_zone[0][0],stopping_zone[0][1]],
                                [stopping_zone[3][0],stopping_zone[3][1]],
                                [driving_path[3][0],driving_path[3][1]+50]], np.int32)

imgcv = cv2.imread(path)
cv2.imwrite("./bounding-boxes.png", imgcv)
imgcv = cv2.imread("./bounding-boxes.png")
cv2.polylines(imgcv, [driving_path], True, (51,240,255), 2)
cv2.polylines(imgcv, [warning_left_sector], True, (51,165,255), 2)
cv2.polylines(imgcv, [warning_right_sector], True, (0,255,255), 2)
cv2.polylines(imgcv, [danger_left_sector], True, (0,255,255), 2)
cv2.polylines(imgcv, [danger_right_sector], True, (0,255,255), 2)
cv2.polylines(imgcv, [stopping_zone], True, (0,255,255), 2)
cv2.polylines(imgcv, [slow_zone], True, (0,255,255), 2)
cv2.imwrite("./bounding-boxes.png", imgcv)



