import os
import sys
from util import *
## Need Python version > 2.7
from collections import Counter
import numpy as np
from darkflow.net.build import TFNet
import cv2
import imageio

##import urllib
if sys.version_info[0] >= 3:
    from urllib.request import urlretrieve
else:
    # Not Python 3 - today, it is most likely to be Python 2
    # But note that this might need an update when Python 4
    # might be around one day
    from urllib import urlretrieve

import base64

def check_label(results, adv_results):
    for result in results:
        deviant = True;
        for advresult in adv_results:
            if(result['label']==advresult['label']):
                if (advresult['topleft']['x']-5<result['topleft']['x']<advresult['topleft']['x']+5 and advresult['topleft']['y']-5<result['topleft']['y']<advresult['topleft']['y']+5):
                    if(advresult['bottomright']['x']-5<result['bottomright']['x']<advresult['bottomright']['x']+5 and advresult['bottomright']['y']-5<result['bottomright']['y']<advresult['bottomright']['y']+5):
                        deviant = False
        if deviant:
            result['label'] = "deviant: "+result['label']

    for advresult in adv_results:
        deviant = True;
        for result in results:
            if(advresult['label']==result['label']):
                if (result['topleft']['x']-5<advresult['topleft']['x']<result['topleft']['x']+5 and result['topleft']['y']-5<advresult['topleft']['y']<result['topleft']['y']+5):
                    if(result['bottomright']['x']-5<advresult['bottomright']['x']<result['bottomright']['x']+5 and result['bottomright']['y']-5<advresult['bottomright']['y']<result['bottomright']['y']+5):
                        deviant = False
        if deviant:
            advresult['label'] = "deviant: "+advresult['label']


## Added different colours for common detected objects
##(will find a better solution for all possible labels later)
def decide_box_colour(str):
    colour_list=[{"label":"person","colour":(255,0,0)},{"label":"bicycle","colour":(0,255,0)},{"label":"car","colour":(0,0,255)},
                 {"label":"bus","colour":(242,198,90)},{"label":"truck","colour":(144,75,154)},{"label":"motorbike","colour":(237,155,16)},
                 {"label":"traffic light", "colour":(255,255,0)}]
    colour = (123,123,123)
    if str.startswith("deviant"):
        colour = (0,0,0)
    for color in colour_list:
        if (str == color["label"]):
            colour = color["colour"]
            break
    return colour

## To draw the bounding boxes for detected objects
def write_boundingboxes(results, imgcv):
    cv2.imwrite("prediction.png", imgcv)
    imgcv = cv2.imread("prediction.png")
    for result in results:
        cv2.rectangle(imgcv,
                     (result["topleft"]["x"], result["topleft"]["y"]),
                     (result["bottomright"]["x"],result["bottomright"]["y"]),
                     decide_box_colour(result["label"]), 2)
        text_x, text_y = int(result["topleft"]["x"]) - 10, int(result["topleft"]["y"]) - 10
        cv2.putText(imgcv, result["label"], (text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX, 0.8, decide_box_colour(result["label"]), 2, cv2.LINE_AA)
    cv2.imwrite("prediction.png", imgcv)

## check safety using darkflow
def check_safety_dflow(step, https, pano, fov, heading, pitch, key):
    if not os.path.exists(str(step)):
        os.makedirs(str(step))
    else:
        print('step {0} exists'.format(step))

    options = {"model": "cfg/yolo.cfg", "load": "bin/yolo.weights", "threshold": 0.3}
    tfnet = TFNet(options)

    url='{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, heading, pitch, key)
    img = "fov{0}heading{1}pitch{2}.png".format(fov, heading, pitch)
    urlretrieve(url, "./{0}/{1}".format(step, img))
    ori_imgcv = cv2.imread("./{0}/{1}".format(step, img))
    results = tfnet.return_predict(ori_imgcv)
    write_boundingboxes(results, ori_imgcv)
    origin_labels = []
    for result in results:
        origin_labels.append(result["label"])
    os.system("cp prediction.png ./{0}/{1}".format(step, img))
    if step>9:
        os.system("cp prediction.png ./images/step{0}.png".format(step))
    else:
        os.system("cp prediction.png ./images/step0{0}.png".format(step))

    ## change the heading
    delta = 0.1
    sigma = 0.01
    for x in np.arange(sigma, delta, sigma):
        adv_found = False
        for b in range(0, 2):
            if b==0: h=heading+x
            else: h=heading-x
            url = '{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, h, pitch, key)
            img = "fov{0}heading{1}pitch{2}.png".format(fov, h, pitch)
            urlretrieve(url, "./{0}/{1}".format(step, img))
            adv_imgcv = cv2.imread("./{0}/{1}".format(step, img))
            adv_results = tfnet.return_predict(adv_imgcv)
            adv_labels = []
            for result in adv_results:
                adv_labels.append(result["label"])
            if not (Counter(origin_labels)==Counter(adv_labels)):
                check_label(results, adv_results)
                write_boundingboxes(results, ori_imgcv)
                os.system("cp prediction.png ./{0}/{1}".format(step, img))
                if step>9:
                    os.system("cp prediction.png ./images/step{0}.png".format(step))
                else:
                    os.system("cp prediction.png ./images/step0{0}.png".format(step))
                write_boundingboxes(adv_results, adv_imgcv)
                os.system("cp prediction.png ./{0}/adv-{1}".format(step, img))
                if step>9:
                    os.system("cp prediction.png ./images/adv-step{0}.png".format(step))
                else:
                    os.system("cp prediction.png ./images/adv-step0{0}.png".format(step))
                os.system("rm ./{0}/{1}".format(step, img))
                adv_found = True
                break
            else:
                os.system("rm ./{0}/{1}".format(step, img))
        if adv_found: return False

    return True

def imgTogif(origin_images, adv_images):
    img_list=[]
    adv_list=[]
    if (len(origin_images) > 0):
        for image in origin_images:
            img_list.append(imageio.imread(image))
        imageio.mimsave('./images/img_out.gif',img_list, duration=1)
    if (len(adv_images) >0):
        for image in adv_images:
            adv_list.append(imageio.imread(image))
        imageio.mimsave('./images/adv_out.gif',adv_list, duration=1)
