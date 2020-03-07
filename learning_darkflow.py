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

# creating the darkflow object detector
options = {"model": "./cfg/yolov2.cfg", "load": "./cfg/bin/yolov2.weights", "threshold": 0.1, "gpu": 1.0}
tfnet = TFNet(options)

prev_objs_in_slow_range = []
prev_objs_in_stop_range = []
objs_in_slow_range = []
objs_in_stop_range = []
car_status = ""
folder = "test_route"
routes = os.listdir("./{0}/".format(folder))
predicted_path = 'predicted_routes'
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

def decide_box_colour(label):
    colour = (0,0,255)
    if label.startswith("danger"):
        colour = (51,165,255)
    if label.startswith("stop"):
        colour = (0,0,255)
    if label.startswith("warning"):
        colour = (51,240,255)
    if label.startswith("slow"):
        colour = (51,165,255)
    return colour

def check_status_of_car():
    status =''
    status = check_stop_zone()
    if status != "driving":
        return status
    status = check_slow_zone()
    return status


def check_stop_zone():
    if len(objs_in_stop_range) > 0:
        return "stopped"
    elif len(prev_objs_in_stop_range) > 0 and len(objs_in_stop_range) == 0:
        return "accelerating"
    else:
        return "driving"

def check_slow_zone():
    if len(prev_objs_in_slow_range) == 0 and len(objs_in_slow_range) > 0 :
        return "decelerating"
    elif len(objs_in_slow_range) > 0:
        objs_in_slow_range.sort()
        if len(prev_objs_in_slow_range) > 0:
            prev_objs_in_slow_range.sort()
            if objs_in_slow_range[-1] > prev_objs_in_slow_range[-1]:
                return "decelerating"
            elif objs_in_slow_range[-1] < prev_objs_in_slow_range[-1]:
                return "accelerating"
            else:
                return "slow"
        else:
            return "slow"
    else:
        return "driving"


def write_boundingboxes(results, imgcv, new_img, car_status):
    for result in results:
        if result['status']=='': continue 
        cv2.rectangle(imgcv,
                     (result["topleft"]["x"], result["topleft"]["y"]),
                     (result["bottomright"]["x"],result["bottomright"]["y"]),
                     decide_box_colour(result["status"]), 2)
    cv2.putText(imgcv, "car status: {0}".format(car_status), (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0))
    cv2.imwrite(new_img, imgcv)

def convertToGif(images, path, route):
    img_list=[]
    if (len(images) > 0):
        for image in images:
            img_list.append(imageio.imread('./{0}/{1}/{2}'.format(path, route, image)))
        imageio.mimsave('./{0}/{1}/journey.gif'.format(path, route),img_list, duration=0.2)

def objectInSector(result, poly, message):
    corners = np.array([[result['topleft']['x'], result['topleft']['y']],
                       [result['bottomright']['x'], result['bottomright']['y']],
                       [result['topleft']['x'], result['bottomright']['y']],
                       [result['bottomright']['x'], result['topleft']['y']]], np.int32)  
    for corner in corners:
        corner = Point(corner)
        if poly.contains(corner):
            return True
    
    return False

def clearObjLists():
    objs_in_slow_range.clear()
    objs_in_stop_range.clear()

def set_prev_obj():
    global prev_objs_in_slow_range
    global prev_objs_in_stop_range
    prev_objs_in_slow_range.clear()
    prev_objs_in_stop_range.clear()
    prev_objs_in_slow_range = objs_in_slow_range.copy()
    prev_objs_in_stop_range = objs_in_stop_range.copy()    

def check_if_object_in_path(results):
    clearObjLists()
    for result in results:
        result['status'] = ''
        if objectInSector(result, Polygon(warning_left_sector), "warning" ) or objectInSector(result, Polygon(warning_right_sector), "warning" ):
            result['status'] = "warning"
        if objectInSector(result, Polygon(danger_left_sector), "danger" ) or objectInSector(result, Polygon(danger_right_sector), "danger" ):
            result['status'] = "danger"
        if objectInSector(result, Polygon(slow_zone), "slow" ):
            result['status'] = "slow"
            add_obj_to_warning_list(result['bottomright']['y'])
        if objectInSector(result, Polygon(stopping_zone), "stop" ):
            result['status'] = "stop"
            add_obj_to_danger_list(result['bottomright']['y'])

    return results
    
def add_obj_to_warning_list(y):
    objs_in_slow_range.append(y)


def add_obj_to_danger_list(y):
    objs_in_stop_range.append(y)



def get_prediction(routes):
    for route in routes:
        steps = os.listdir('./{0}/{1}/'.format(folder,route))
        steps = sorted(steps)
        for step in steps:
            imgcv = cv2.imread('./{0}/{1}/{2}'.format(folder,route, step))
            print("starting prediction")
            results = tfnet.return_predict(imgcv)
            print("results collected")
            results = check_if_object_in_path(results)
            car_status = check_status_of_car()
            set_prev_obj()
            if os.path.exists('./{0}/{1}/'.format(predicted_path, route)):
                write_boundingboxes(results, imgcv, './{0}/{1}/{2}'.format(predicted_path, route, step), car_status)
            else:
                try:
                    os.mkdir('./{0}/{1}/'.format(predicted_path, route))
                    write_boundingboxes(results, imgcv, './{0}/{1}/{2}'.format(predicted_path,route, step), car_status)
                except OSError:
                    print ("Creation of the directory ./{0}/{1} failed".format(predicted_path, route))
                else:
                    print ("Successfully created the directory ./{0}/{1}".format(predicted_path, route))
        predicted_route = os.listdir("./{0}/{1}/".format(predicted_path, route))
        predicted_route = sorted(predicted_route)
        convertToGif(predicted_route, predicted_path, route)


get_prediction(routes)



