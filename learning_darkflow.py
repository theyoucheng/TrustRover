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

#creating the darkflow object detector
options = {"model": "./cfg/yolo.cfg", "load": "./cfg/bin/yolo.weights", "threshold": 0.3, "gpu": 0.6}
tfnet = TFNet(options)

routes = os.listdir("./test_route/")
predicted_path = 'predicted_routes'
driving_path = np.array([[180,195],[100,400],[300,400],[190,195]], np.int32)
warning_path = np.array([[210,195],[180,300],[270,300],[220,195]], np.int32)
danger_path = np.array([[180,300],[130,400],[330,400],[270,300]], np.int32)
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

def decide_box_colour(label):
    colour = (0,0,255)
    colour_list=[{"label":"person","colour":(255,0,0)},{"label":"bicycle","colour":(0,255,0)},{"label":"car","colour":(0,255,0)},
                {"label":"bus","colour":(242,198,90)},{"label":"truck","colour":(144,75,154)},{"label":"motorbike","colour":(237,155,16)},
                {"label":"traffic light", "colour":(255,255,0)}]
    for obj in colour_list:
        if label==obj["label"]: colour = obj["colour"]
    if colour =='': colour = (0,0,255)
    if label.startswith("danger"):
        colour = (0,0,255)
    if label.startswith("warning"):
        colour = (51,165,255)
    return colour

def write_boundingboxes(results, imgcv, new_img):
    cv2.imwrite(new_img, imgcv)
    imgcv = cv2.imread(new_img)
    ## ROI: region of interest
    vtx = driving_path
    vtx2 = warning_left_sector
    vtx3 = danger_left_sector
    vtx4 = warning_right_sector
    vtx5 = danger_right_sector
    cv2.polylines(imgcv, [vtx], True, (255,255,255), 2)
    cv2.polylines(imgcv, [vtx2], True, (51,165,255), 2)
    cv2.polylines(imgcv, [vtx3], True, (0,0,255), 2)
    cv2.polylines(imgcv, [vtx4], True, (51,165,255), 2)
    cv2.polylines(imgcv, [vtx5], True, (0,0,255), 2)
    results = check_if_object_in_path(results)
    for result in results:
        if result['label']=='': continue 
        cv2.rectangle(imgcv,
                     (result["topleft"]["x"], result["topleft"]["y"]),
                     (result["bottomright"]["x"],result["bottomright"]["y"]),
                     decide_box_colour(result["label"]), 2)
        text_x, text_y = int(result["topleft"]["x"]) - 10, int(result["topleft"]["y"]) - 10
        cv2.putText(imgcv, result["label"], (text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, decide_box_colour(result['label']), 2, cv2.LINE_AA)
        cv2.imwrite(new_img, imgcv)

def convertToGif(images, path, route):
    img_list=[]
    if (len(images) > 0):
        for image in images:
            img_list.append(imageio.imread('./{0}/{1}/{2}'.format(path, route, image)))
        imageio.mimsave('./{0}/{1}/journey.gif'.format(path, route),img_list, duration=0.2)

def check_if_object_in_path(results):
    for result in results:
        inside = False
        point1 = Point(result['topleft']['x'], result['topleft']['y'])
        point2 = Point(result['bottomright']['x'], result['bottomright']['y'])
        point3 = Point(result['topleft']['x'], result['bottomright']['y'])
        point4 = Point(result['bottomright']['x'], result['topleft']['y'])
        warning_poly = Polygon(warning_path)
        danger_poly = Polygon(danger_path)
        left_warning_poly = Polygon(warning_left_sector)
        left_danger_poly = Polygon(danger_left_sector)
        right_warning_poly = Polygon(warning_right_sector)
        right_danger_poly = Polygon(danger_right_sector)
        if warning_poly.contains(point1):
            result['label'] = 'warning {0}'.format(result['label'])
        elif warning_poly.contains(point2):
            result['label'] = 'warning {0}'.format(result['label'])
        elif warning_poly.contains(point3):
            result['label'] = 'warning {0}'.format(result['label'])
        elif warning_poly.contains(point4):
            result['label'] = 'warning {0}'.format(result['label'])
        
        if left_warning_poly.contains(point1):
            result['label'] = 'warning {0}'.format(result['label'])
        elif left_warning_poly.contains(point2):
            result['label'] = 'warning {0}'.format(result['label'])
        elif left_warning_poly.contains(point3):
            result['label'] = 'warning {0}'.format(result['label'])
        elif left_warning_poly.contains(point4):
            result['label'] = 'warning {0}'.format(result['label'])
        
        if right_warning_poly.contains(point1):
            result['label'] = 'warning {0}'.format(result['label'])
        elif right_warning_poly.contains(point2):
            result['label'] = 'warning {0}'.format(result['label'])
        elif right_warning_poly.contains(point3):
            result['label'] = 'warning {0}'.format(result['label'])
        elif right_warning_poly.contains(point4):
            result['label'] = 'warning {0}'.format(result['label'])
        
        if danger_poly.contains(point1):
            result['label'] = 'danger {0}'.format(result['label'])
        elif danger_poly.contains(point2):
            result['label'] = 'danger {0}'.format(result['label'])
        elif danger_poly.contains(point3):
            result['label'] = 'danger {0}'.format(result['label'])
        elif danger_poly.contains(point4):
            result['label'] = 'danger {0}'.format(result['label'])

        if left_danger_poly.contains(point1):
            result['label'] = 'danger {0}'.format(result['label'])
        elif left_danger_poly.contains(point2):
            result['label'] = 'danger {0}'.format(result['label'])
        elif left_danger_poly.contains(point3):
            result['label'] = 'danger {0}'.format(result['label'])
        elif left_danger_poly.contains(point4):
            result['label'] = 'danger {0}'.format(result['label'])

        if right_danger_poly.contains(point1):
            result['label'] = 'danger {0}'.format(result['label'])
        elif right_danger_poly.contains(point2):
            result['label'] = 'danger {0}'.format(result['label'])
        elif right_danger_poly.contains(point3):
            result['label'] = 'danger {0}'.format(result['label'])
        elif right_danger_poly.contains(point4):
            result['label'] = 'danger {0}'.format(result['label'])
    return results


def get_prediction(routes):

    for route in routes:
        steps = os.listdir('./test_route/{0}/'.format(route))
        steps = sorted(steps)
        for step in steps:
            imgcv = cv2.imread('./test_route/{0}/{1}'.format(route, step))
            results = tfnet.return_predict(imgcv)
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


