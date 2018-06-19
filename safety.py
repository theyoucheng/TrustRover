import os
import sys
from util import *
import numpy as np

##import urllib
if sys.version_info[0] >= 3:
    from urllib.request import urlretrieve
else:
    # Not Python 3 - today, it is most likely to be Python 2
    # But note that this might need an update when Python 4
    # might be around one day
    from urllib import urlretrieve

import base64

def check_safety(step, https, pano, fov, heading, pitch, key):
  if not os.path.exists(str(step)):
    os.makedirs(str(step))
  else:
    print ('step {0} exists'.format(step))
  c=0
  url='{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, heading, pitch, key)
  urlretrieve(url,  "./{0}/{1}.png".format(step, c)) #, "./{0}/{1}.png".format(step, c))
  print ("./darknet detect cfg/yolov3.cfg yolov3.weights ./{0}/0.png".format(step))
  #os.system("./darknet detect cfg/yolov3-tiny.cfg yolov3-tiny.weights ./{0}/0.png".format(step))
  os.system("./darknet detect cfg/yolov3.cfg yolov3.weights ./{0}/0.png".format(step))
  os.system("cp predictions.png ./{0}".format(step))
  os.system("cp predictions.png ./images/step{0}.png".format(step))


def check_robust_safety(step, https, pano, fov, heading, pitch, key):
  if not os.path.exists(str(step)):
    os.makedirs(str(step))
  else:
    print ('step {0} exists'.format(step))

  url='{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, heading, pitch, key)

  ## the image name
  img="fov{0}heading{1}pitch{2}.png".format(fov, heading, pitch)
  urlretrieve(url,  "./{0}/{1}".format(step, img))
  print ("./darknet detect cfg/yolov3.cfg yolov3.weights ./{0}/{1}.png".format(step, img))

  #os.system("./darknet detect cfg/yolov3.cfg yolov3.weights ./{0}/{1} > ./{0}/logs".format(step, img))
  os.system("./darknet detect cfg/yolov3-tiny.cfg yolov3-tiny.weights ./{0}/{1} > ./{0}/logs".format(step, img))
  labels=read_yolo_labels("./{0}/logs".format(step))
  os.system("cp predictions.png ./{0}/{1}".format(step, img))
  os.system("cp predictions.png ./{0}/0.png".format(step))
  if step>9:
    os.system("cp predictions.png ./images/step{0}.png".format(step))
  else:
    os.system("cp predictions.png ./images/step0{0}.png".format(step))

  ### heading +/- 
  #delta=0.1
  #sigma=0.01
  ##for h in np.arange(heading-delta, heading+delta+sigma, sigma):
  #for x in np.arange(sigma, delta, sigma):
  #  adv_found=False
  #  for b in range(0, 2):
  #    if b==0: h=heading+x
  #    else: h=heading-x
  #    #print '####', (h-heading)
  #    url='{0}&pano={1}&fov={2}&heading={3}&pitch={4}&key={5}'.format(https, pano, fov, h, pitch, key)
  #    ## the image name
  #    img="fov{0}heading{1}pitch{2}.png".format(fov, h, pitch)
  #    urlretrieve(url,  "./{0}/{1}".format(step, img)) 
  #    os.system("./darknet detect cfg/yolov3.cfg yolov3.weights ./{0}/{1} > ./{0}/logs".format(step, img))
  #    h_labels=read_yolo_labels("./{0}/logs".format(step))
  #    if not (labels==h_labels):
  #      os.system("rm ./{0}/{1}".format(step, img))
  #      os.system("cp predictions.png ./{0}/adv-{1}".format(step, img))
  #      print h_labels, labels
  #      if step>9:
  #        os.system("cp predictions.png ./adv-images/step{0}.png".format(step, step))
  #      else:
  #        os.system("cp predictions.png ./adv-images/step0{0}.png".format(step, step))
  #      adv_found=True
  #      break
  #    else:
  #      os.system("rm ./{0}/{1}".format(step, img))
  #      #os.system("cp predictions.png ./{0}/{1}".format(step, img))
  #  if adv_found: break

  ##os.system("cp predictions.png ./{0}".format(step))
  ##os.system("cp predictions.png ./images/step{0}.png".format(step))


