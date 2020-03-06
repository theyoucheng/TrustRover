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

objs_in_range = np.empty((3,2))
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
        colour = (0,0,255)
    if label.startswith("warning"):
        colour = (51,165,255)
    return colour

def check_status_of_car(num_of_pos_collision, num_of_obj_ahead):
    if num_of_pos_collision > 0:
        return "stopped"
    elif num_of_obj_ahead > 0:
        return "slow"
    else :
        return "driving"

def write_boundingboxes(results, imgcv, new_img):
    # cv2.imwrite(new_img, imgcv)
    # imgcv = cv2.imread(new_img)
    ## ROI: region of interest
    num_of_pos_collision = 0
    num_of_obj_ahead = 0
    results = check_if_object_in_path(results)
    for result in results:
        if result['status']=='': continue 
        cv2.rectangle(imgcv,
                     (result["topleft"]["x"], result["topleft"]["y"]),
                     (result["bottomright"]["x"],result["bottomright"]["y"]),
                     decide_box_colour(result["status"]), 2)
        text_x, text_y = int(result["topleft"]["x"]) - 10, int(result["topleft"]["y"]) - 10
        cv2.putText(imgcv, result["label"], (text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, decide_box_colour(result['status']), 2, cv2.LINE_AA)
        if result['status'] == 'stop': 
            num_of_pos_collision += 1
        if result['status'] == 'slow': 
            num_of_obj_ahead += 1
            add_obj_to_warning_list(result["topleft"]["y"])

    car_status = check_status_of_car(num_of_pos_collision,num_of_obj_ahead)
    cv2.putText(imgcv, "car status: {0}".format(car_status), (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
    cv2.putText(imgcv, "objs in warning: {0}".format(objs_in_range.size), (250, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)

    cv2.imwrite(new_img, imgcv)

def convertToGif(images, path, route):
    img_list=[]
    if (len(images) > 0):
        for image in images:
            img_list.append(imageio.imread('./{0}/{1}/{2}'.format(path, route, image)))
        imageio.mimsave('./{0}/{1}/journey.gif'.format(path, route),img_list, duration=0.2)

def objectInSector(result, poly, message):
    point1 = Point(result['topleft']['x'], result['topleft']['y'])
    point2 = Point(result['bottomright']['x'], result['bottomright']['y'])
    point3 = Point(result['topleft']['x'], result['bottomright']['y'])
    point4 = Point(result['bottomright']['x'], result['topleft']['y'])
    if poly.contains(point1):
        result['status'] = message
    elif poly.contains(point2):
        result['status'] = message
    elif poly.contains(point3):
        result['status'] = message
    elif poly.contains(point4):
        result['status'] = message
    return result



def check_if_object_in_path(results):
    for result in results:
        result['status'] = ''
        result = objectInSector(result, Polygon(warning_left_sector), "warning" )
        result = objectInSector(result, Polygon(warning_right_sector), "warning" )
        result = objectInSector(result, Polygon(danger_left_sector), "danger" )
        result = objectInSector(result, Polygon(danger_right_sector), "danger" )
        result = objectInSector(result, Polygon(stopping_zone), "stop" )
        result = objectInSector(result, Polygon(slow_zone), "slow" )   
    return results
    
def add_obj_to_warning_list(y):
    np.append(objs_in_range,y)


def get_prediction(routes):

    for route in routes:
        steps = os.listdir('./{0}/{1}/'.format(folder,route))
        steps = sorted(steps)
        for step in steps:
            imgcv = cv2.imread('./{0}/{1}/{2}'.format(folder,route, step))
            print("starting prediction")
            results = tfnet.return_predict(imgcv)
            print("results collected")
            if os.path.exists('./{0}/{1}/'.format(predicted_path, route)):
                write_boundingboxes(results, imgcv, './{0}/{1}/{2}'.format(predicted_path, route, step))
            else:
                try:
                    os.mkdir('./{0}/{1}/'.format(predicted_path, route))
                    write_boundingboxes(results, imgcv, './{0}/{1}/{2}'.format(predicted_path,route, step))
                except OSError:
                    print ("Creation of the directory ./{0}/{1} failed".format(predicted_path, route))
                else:
                    print ("Successfully created the directory ./{0}/{1}".format(predicted_path, route))
        predicted_route = os.listdir("./{0}/{1}/".format(predicted_path, route))
        predicted_route = sorted(predicted_route)
        convertToGif(predicted_route, predicted_path, route)


get_prediction(routes)



