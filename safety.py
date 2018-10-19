import os
import sys
from util import *
import math
## Need Python version > 2.7
from collections import Counter
import numpy as np
from darkflow.net.build import TFNet
import cv2
import imageio
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

##import urllib
if sys.version_info[0] >= 3:
    from urllib.request import urlretrieve
else:
    # Not Python 3 - today, it is most likely to be Python 2
    # But note that this might need an update when Python 4
    # might be around one day
    from urllib import urlretrieve

import base64

def check_inside(results):
    closest = 0
    for result in results:
        inside = False
        point1 = Point(result['topleft']['x'], result['topleft']['y'])
        point2 = Point(result['bottomright']['x'], result['bottomright']['y'])
        poly = Polygon([(320,370),(640,470),(640,640),(0,640),(0,525)])
        distance = 640 - result['bottomright']['y']
        if poly.contains(point1):
            inside = True
        if poly.contains(point2):
            inside = True
        if inside:
            meters = math.pow(2, distance/27)/10
            #result['label'] = 'danger: '+result['label']+' ('+f'{meters:.3f}'+'m)'
            if closest == 0 or closest>meters:
                closest = meters
        else:
            result['label'] = ''
    if closest == 0: acc = 0
    else: acc = -(25*25)/(2*closest)
    return acc


def check_label(results, adv_results):

    for result in results:
        deviant = True
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

#def close(x,y):
#  d=25
#  return (y-d<=x and x<=y+d) or (x-d<=y and y<=x+d)

def close(topleft1, bottomright1, topleft2, bottomright2):
  print ('in close')

  xt1=topleft1['x']
  yt1=topleft1['y']
  xt2=topleft2['x']
  yt2=topleft2['y']

  xb1=bottomright1['x']
  yb1=bottomright1['y']
  xb2=bottomright2['x']
  yb2=bottomright2['y']

  boxA=[xt1,yt1,xb1,yb1]
  boxB=[xt2,yt2,xb2,yb2]
  # determine the (x, y)-coordinates of the intersection rectangle
  xA = max(boxA[0], boxB[0])
  yA = max(boxA[1], boxB[1])
  xB = min(boxA[2], boxB[2])
  yB = min(boxA[3], boxB[3])
  
  # compute the area of intersection rectangle
  interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
  
  # compute the area of both the prediction and ground-truth
  # rectangles
  boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
  boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
  
  # compute the intersection over union by taking the intersection
  # area and dividing it by the sum of prediction + ground-truth
  # areas - the interesection area
  iou = interArea / float(boxAArea + boxBArea - interArea)
  
  print (boxAArea, boxBArea, boxA, boxB, iou)
  # return the intersection over union value
  return iou>0.5

  #h1=-(yt1-yb1)
  #w1=-(xt1-xb1)
  #print ('===>',h1,w1)
  #h2=-(yt2-yb2)
  #w2=-(xt2-xb2)

  #f=1

  #if xt1-w1*f <= xt2 <= xt1+w1*f and yt1-h1*f <= yt2 <= yt1+h1*f:
  #  if xb1-w1*f <= xb2 <= xb1+w1*f and yb1-h1*f <= yb2 <= yb1+h1*f:
  #    if xt2-w2*f <= xt1 <= xt2+w2*f and yt2-h2*f <= yt1 <= yt2+h2*f:
  #      if xb2-w2*f <= xb1 <= xb2+w2*f and yb2-h2*f <= yb1 <= yb2+h2*f:
  #        return True

  ##if topleft1['x']-w1*0.1<=topleft2['x'] and topleft2['x']<=topleft1['x']+w1*0.1:
  ##  if topleft1['x']-h1*0.1<=topleft2['x'] and topleft2['y']<=topleft1['y']+h1*0.1:
  ##    pass
  #return False
  

def diff(results, adv_results):

  new_adv_results=[]
  diff_results=[]

  print ('###',results, adv_results)

  for result in results:
    if result['label']=='': continue
    deviant = True
    for advresult in adv_results:
      overlapping=False
      print ('+++++++++++++++',result['label'],advresult['label'])
      if close(advresult['topleft'],advresult['bottomright'],result['topleft'],result['bottomright']):
        overlapping=True
      if overlapping:
          deviant = False
          break
    ## result is not detected in the adv case
    if deviant == True:
      nonrobust_result=result.copy()
      nonrobust_result['label'] = "nonrobust: "+nonrobust_result['label']
      diff_results.append(nonrobust_result)

  for advresult in adv_results:
    if advresult['label']=='': continue
    deviant = True;
    for result in results:
      overlapping=False
      print ('----------------',result['label'],advresult['label'])
      if close(advresult['topleft'],advresult['bottomright'],result['topleft'],result['bottomright']):
        overlapping=True
      if overlapping:
        if(advresult['label']==result['label']):
          deviant = False
        break
    result=advresult.copy()
    ## advresult is not in the original results
    if deviant:
      result['label'] = "nonrobust: "+result['label']
    diff_results.append(result)

  return diff_results

## Added different colours for common detected objects
##(will find a better solution for all possible labels later)
def decide_box_colour(str):
    ##colour_list=[{"label":"person","colour":(255,0,0)},{"label":"bicycle","colour":(0,255,0)},{"label":"car","colour":(0,0,255)},
    ##             {"label":"bus","colour":(242,198,90)},{"label":"truck","colour":(144,75,154)},{"label":"motorbike","colour":(237,155,16)},
    ##             {"label":"traffic light", "colour":(255,255,0)}]
    colour = (0,255,0)
    if str.startswith("danger") or str.startswith("nonrobust"):
        colour = (0,0,255)
    return colour

## To draw the bounding boxes for detected objects
def write_boundingboxes(results, imgcv):
    cv2.imwrite("prediction.png", imgcv)
    imgcv = cv2.imread("prediction.png")
    ## ROI: region of interest
    vtx = np.array([[320,370],[640,470],[640,640],[0,640],[0,525]], np.int32)
    cv2.polylines(imgcv, [vtx], True, (0,255,255), 2)
    for result in results:
        if result['label']=='': continue
        cv2.rectangle(imgcv,
                     (result["topleft"]["x"], result["topleft"]["y"]),
                     (result["bottomright"]["x"],result["bottomright"]["y"]),
                     decide_box_colour(result["label"]), 2)
        text_x, text_y = int(result["topleft"]["x"]) - 10, int(result["topleft"]["y"]) - 10
        cv2.putText(imgcv, result["label"], (text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX, 0.8, decide_box_colour(result["label"]), 2, cv2.LINE_AA)
    cv2.imwrite("prediction.png", imgcv)

## To draw the bounding boxes for detected objects
def new_write_boundingboxes(results, imgcv, new_img):
    cv2.imwrite(new_img, imgcv)
    imgcv = cv2.imread(new_img)
    ## ROI: region of interest
    vtx = np.array([[320,370],[640,470],[640,640],[0,640],[0,525]], np.int32)
    cv2.polylines(imgcv, [vtx], True, (0,255,255), 2)
    for result in results:
        if result['label']=='': continue
        cv2.rectangle(imgcv,
                     (result["topleft"]["x"], result["topleft"]["y"]),
                     (result["bottomright"]["x"],result["bottomright"]["y"]),
                     decide_box_colour(result["label"]), 2)
        text_x, text_y = int(result["topleft"]["x"]) - 10, int(result["topleft"]["y"]) - 10
        cv2.putText(imgcv, result["label"], (text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX, 0.8, decide_box_colour(result["label"]), 2, cv2.LINE_AA)
    cv2.imwrite(new_img, imgcv)

## check safety using darkflow
def check_safety_dflow(step, https, pano, fov, heading, pitch, key, tfnet):

    if not os.path.exists(str(step)):
        os.makedirs(str(step))
    else:
        print('step {0} exists'.format(step))

    ## image url
    url='{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, heading, pitch, key)
    ## image name
    img = 'step{0}.png'.format(step) #"fov{0}heading{1}pitch{2}".format(fov, heading, pitch)
    origin_img = 'origin_step{0}'.format(step) #"fov{0}heading{1}pitch{2}".format(fov, heading, pitch)
    ## to retrieve the image
    urlretrieve(url, "./{0}/{1}".format(step, origin_img))


    ## the image is read
    imgcv = cv2.imread("./{0}/{1}".format(step, origin_img))
    ## let's predict
    results = tfnet.return_predict(imgcv)

    check_inside(results)

    ## draw the bounding box
    new_write_boundingboxes(results, imgcv, './{0}/{1}'.format(step, img))
    if step>9:
        os.system("cp ./{0}/step{0}.png ./images/step{0}.png".format(step))
    else:
        os.system("cp ./{0}/step{0}.png ./images/step0{0}.png".format(step))

    origin_labels = []
    for result in results:
        if not result['label']=='':
          origin_labels.append(result["label"])


    ## let us change the heading
    delta = 0.1
    sigma = 0.01
    for x in np.arange(sigma, delta, sigma):
      adv_found = False
      for b in range(0, 2):
        if b==0: h=heading+x
        else: h=heading-x
        url = '{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, h, pitch, key)
        ## the heading adjusted image
        advimg = 'heading_step{0}'.format(step) #"heading_fov{0}heading{1}pitch{2}.png".format(fov, h, pitch)
        urlretrieve(url, "./{0}/{1}".format(step, advimg))
        adv_imgcv = cv2.imread("./{0}/{1}".format(step, advimg))

        adv_results = tfnet.return_predict(adv_imgcv)
        check_inside(adv_results)

        adv_labels = []
        for result in adv_results:
          if not result['label']=='':
            adv_labels.append(result["label"])

        ## inconsistency
        if not (Counter(origin_labels)==Counter(adv_labels)):
          print ('==============================', step)
          adv_results=diff(results, adv_results)
          new_write_boundingboxes(adv_results, adv_imgcv, './{0}/adv_'.format(step)+img)
          if step>9:
              os.system("cp ./{0}/adv_step{0}.png ./images/adv_step{0}.png".format(step))
          else:
              os.system("cp ./{0}/adv_step{0}.png ./images/adv_step0{0}.png".format(step))
          adv_found = True
        os.system("rm ./{0}/{1}".format(step, advimg))
        if adv_found: return False

    ## It's safe!
    if step>9:
        os.system("cp ./{0}/step{0}.png ./images/adv_step{0}.png".format(step))
    else:
        os.system("cp ./{0}/step{0}.png ./images/adv_step0{0}.png".format(step))

    ## do not continue
    return True

    for x in np.arange(sigma, delta, sigma):
        for b in range(0, 2):
            if b==0: f=fov+x
            else: f=fov-x
            url = '{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, f, heading, pitch, key)
            advimg = "fov{0}heading{1}pitch{2}.png".format(f,heading,pitch)
            urlretrieve(url, "./{0}/{1}".format(step, advimg))
            adv_imgcv = cv2.imread("./{0}/{1}".format(step, advimg))
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
                os.system("cp prediction.png ./{0}/adv-{1}".format(step, advimg))
                if step>9:
                    os.system("cp prediction.png ./images/adv-step{0}.png".format(step))
                else:
                    os.system("cp prediction.png ./images/adv-step0{0}.png".format(step))
                os.system("rm ./{0}/{1}".format(step, advimg))
                adv_found = True
                break
            else:
                os.system("rm ./{0}/{1}".format(step, advimg))
        if adv_found: return False

    for x in np.arange(sigma, delta, sigma):
        for b in range(0, 2):
            if b==0: p=pitch+x
            else: p=pitch-x
            url = '{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, heading, p, key)
            advimg = "fov{0}heading{1}pitch{2}.png".format(fov,heading,p)
            urlretrieve(url, "./{0}/{1}".format(step, advimg))
            adv_imgcv = cv2.imread("./{0}/{1}".format(step, advimg))
            adv_results = tfnet.return_predict(adv_imgcv)
            adv_labels = []
            for result in adv_results:
                adv_labels.append(result["label"])
            ## inconsistent detection result
            if not (Counter(origin_labels)==Counter(adv_labels)):
                check_label(results, adv_results)
                write_boundingboxes(results, ori_imgcv)
                os.system("cp prediction.png ./{0}/{1}".format(step, img))
                if step>9:
                    os.system("cp prediction.png ./images/step{0}.png".format(step))
                else:
                    os.system("cp prediction.png ./images/step0{0}.png".format(step))
                write_boundingboxes(adv_results, adv_imgcv)
                os.system("cp prediction.png ./{0}/adv-{1}".format(step, advimg))
                if step>9:
                    os.system("cp prediction.png ./images/adv-step{0}.png".format(step))
                else:
                    os.system("cp prediction.png ./images/adv-step0{0}.png".format(step))
                os.system("rm ./{0}/{1}".format(step, advimg))
                adv_found = True
                break
            else:
                os.system("rm ./{0}/{1}".format(step, advimg))
        if adv_found: return False
    return True

## TODO: #fix#
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

def darkflow_check(step, https, pano, fov, heading, pitch, key, tfnet):

    if not os.path.exists(str(step)):
        os.makedirs(str(step))
    else:
        print('step {0} exists'.format(step))

    url='{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, heading, pitch, key)
    ## the image name
    img = "fov{0}heading{1}pitch{2}.png".format(fov, heading, pitch)
    ## to retrieve the image
    urlretrieve(url, "./{0}/{1}".format(step, img))
    ## the retrieved image
    ori_imgcv = cv2.imread("./{0}/{1}".format(step, img))
    ## the object detection
    results = tfnet.return_predict(ori_imgcv)
    ## check these objects inside the region of interest
    acc = check_inside(results)
    acctext = "The accelaration must < "+f'{acc:.2f}'+"m/t^2"
    ## draw the bounding box
    write_boundingboxes(results, ori_imgcv)
    #### why???
    predic = cv2.imread("prediction.png")
    cv2.putText(predic, acctext, (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 1, cv2.LINE_AA)
    cv2.imwrite("prediction.png",predic)
    os.system("cp prediction.png ./{0}/{1}".format(step, img))
    ####
    #### to copy into the images archieve
    print ('== to copy into the images archieve')
    if step>9:
        os.system("cp prediction.png ./images/step{0}.png".format(step))
    else:
        os.system("cp prediction.png ./images/step0{0}.png".format(step))

    distance = 0
    adj_heading = 0
    for result in results:
        if not result['label']=='': #result['label'].startswith("danger"):
            obj_pos = (result['bottomright']['x']+result['topleft']['x'])/2
            distance += (320 - obj_pos)
            if distance > 0:
                adj_heading += (320-distance)/32
            else:
                adj_heading += (-320-distance)/32
    adj_heading += heading
    url='{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, adj_heading, pitch, key)
    advimg = "fov{0}heading{1}pitch{2}.png".format(fov, adj_heading, pitch)
    urlretrieve(url, "./{0}/{1}".format(step, advimg))
    adv_imgcv = cv2.imread("./{0}/{1}".format(step, advimg))
    adv_results = tfnet.return_predict(adv_imgcv)
    check_inside(adv_results)
    write_boundingboxes(adv_results, adv_imgcv)
    os.system("cp prediction.png ./{0}/{1}".format(step, advimg))
    if step>9:
        os.system("cp prediction.png ./images/adv-step{0}.png".format(step))
    else:
        os.system("cp prediction.png ./images/adv-step0{0}.png".format(step))

    return (results, adv_results, adj_heading)
