# This is the simulator class
# this class generates the decision maker and vehicle
# once the predictiosn and decisions have been made
# this class draws out the bounding box of all relevent objects and car status

import os
import sys

import cv2
import numpy as np
import imageio
import json
from darkflow.net.build import TFNet
from car import car
from decision_maker import decision_maker

# logs a string to the console
def log_to_console(message):
    print(message)

# generates and returns the object detector based on the model selected by the user
def set_up_darkflow(model, weights, threshold, GPU):
    log_to_console("starting model")
    options = {"model": model, "load": weights, "threshold": threshold, "gpu": GPU}
    tfnet = TFNet(options)
    return tfnet

# function takes in the object detector and image and returns all oin that image 
def predict_image(image, tfnet):
    results = tfnet.return_predict(image)
    return results

# gets the pre gather routes from the folders. returns the images of the selected route
def get_images(path):
    log_to_console("getting steps from {0}".format(path))
    #gets images
    steps = os.listdir(path)
    # sorts images so they are in order
    steps = sorted(steps)
    log_to_console("steps gathered")
    return steps

# converts list of images to gif
def convertToGif(images, path):
    log_to_console("converting to gif")
    img_list=[]
    if (len(images) > 0):
        for image in images:
            img_list.append(imageio.imread('{0}/{1}'.format(path, image)))
        imageio.mimsave('{0}/journey.gif'.format(path),img_list, duration=0.2)

# decides what colour the object bounding box should be based on status of object
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

#  draws all the bounding boxes of the objects that have been detected in the different driving sectors
#  also draws car status on image as text
def write_boundingboxes(results, imgcv, new_img, car_status):
    for result in results:
        if result['status']=='': continue 
        # draws bounding box per object
        cv2.rectangle(imgcv,
                     (result["topleft"]["x"], result["topleft"]["y"]),
                     (result["bottomright"]["x"],result["bottomright"]["y"]),
                     decide_box_colour(result["status"]), 2)
    # adds car status as text to image
    cv2.putText(imgcv, "car status: {0}".format(car_status), (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,0))
    cv2.imwrite(new_img, imgcv)

# gets the object detector parameters based on user selected model
def get_yolo_params(yolo):
    model = ""
    weights = ""
    threshold = 0.5
    GPU = 1.0
    if yolo == '1.0':  
        model = "./cfg/yolo.cfg"
        weights = "./cfg/bin/yolo.weights"
        threshold = 0.4
        GPU = 1.0
        return model, weights, threshold, GPU
    elif yolo == '2.0':
        model = "./cfg/yolov2.cfg"
        weights = "./cfg/bin/yolov2.weights"
        threshold = 0.4
        GPU = 1.0
        return model, weights, threshold, GPU
    elif yolo =='tiny':
        model = "./cfg/tiny-yolo-voc.cfg"
        weights = "./cfg/bin/tiny-yolo-voc.weights"
        threshold = 0.1
        GPU = 1.0
        return model, weights, threshold, GPU
    else:
        return model, weights, threshold, GPU

# starts the simulator
def run(route, yolo):
   log_to_console("starting simulator")
   model, weights, threshold, GPU = get_yolo_params(yolo)      
   tfnet = set_up_darkflow(model, weights, threshold, GPU)
   path = './routes/{0}'.format(route)
   predictedpath = './completed_routes/{0}/'.format(route)
   steps = get_images(path)
   log_to_console("creating car")
#  arrays below outline the different driving sectors
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
   driving_car = car(driving_path, warning_left_sector, danger_left_sector, 
             warning_right_sector, danger_right_sector, 
             stopping_zone, slow_zone)
   log_to_console("car created")
   log_to_console("creating decision")
#    decision maker object is created
   decisions = decision_maker(driving_car)
   log_to_console("decision maker created")
   log_to_console("starting the analysis")
#    loops through each image from the route, predicts and creates new image with objects and status drawn on it
   for step in steps:
            imgcv = cv2.imread('{0}/{1}'.format(path, step))
            print("starting prediction")
            results = predict_image(imgcv, tfnet)
            print("results collected")
            results = decisions.check_if_object_in_path(results)
            decisions.car.status = decisions.check_status_of_car()
            decisions.set_prev_obj()
            # created folder to contain new simulated images
            if os.path.exists(predictedpath):
                write_boundingboxes(results, imgcv, '{0}/{1}'.format(predictedpath, step), decisions.car.status)
            else:
                try:
                    os.mkdir(predictedpath)
                    write_boundingboxes(results, imgcv, '{0}/{1}'.format(predictedpath, step), decisions.car.status)
                except OSError:
                    print ("Creation of the directory {0} failed".format(predictedpath))
                else:
                    print ("Successfully created the directory {0}".format(predictedpath))
    # takes new images and converts to gif
   predicted_route = os.listdir(predictedpath)
   predicted_route = sorted(predicted_route)
   convertToGif(predicted_route, predictedpath)


        