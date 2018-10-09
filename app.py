from flask import Flask, render_template
from flask import jsonify, request
import flask
from safety import check_safety_dflow
from safety import imgTogif
from safety import darkflow_check
from darkflow.net.build import TFNet
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import csv

import urllib
class Path:

    def __init__(self, name):
        self.name = name
        self.headings = []
        self.objects = []

    def add_heading(self, heading):
        self.headings.append(heading)

    def add_object(self, object):
        self.objects.append(object)

count=-1
origin_images=[]
adv_images=[]
difference_heading=[]
difference_object=[]
new_heading = 0
ori_path = Path('Original')
adv_path = Path('Adv')

options = {"model": "cfg/yolo.cfg", "load": "bin/yolo.weights", "threshold": 0.4}
tfnet = TFNet(options)

app=Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.debug=True

@app.route('/', methods=['GET', 'POST'])
def index():
  return render_template('index.html')

@app.route('/_add_numbers')
def add_numbers():
  a = request.args.get('a', 0, type=int)
  b = request.args.get('b', 0, type=int)
  print (a, b)
  return jsonify(result=a + b)

@app.route('/_check_image')
def check_image():
  ori_l=[]
  adv_l=[]

  u = request.args.get('u', 0, type=str)


  https = request.args.get('https', 0, type=str)
  l_pano = request.args.get('l_pano', 0, type=str)
  fov = request.args.get('fov', 0, type=str)
  heading = request.args.get('heading', 0, type=str)
  pitch = request.args.get('pitch', 0, type=str)
  key = request.args.get('key', 0, type=str)

  ori_path.add_heading(heading)

  global count

  count+=1
  step_name='step{0}.png'.format(count)
  if count<10:
    step_name='step0{0}.png'.format(count)
  adv_found=check_safety_dflow(count, https, l_pano, float(fov), float(heading), float(pitch), key, tfnet)

  #results = darkflow_check(count, https, l_pano, float(fov), float(heading), float(pitch), key, tfnet)
  #adv_heading = results[2]
  #count+=1
  #for result in results[0]:
  #  ori_l.append(result['label'])
  #for result in results[1]:
  #  adv_l.append(result['label'])
  #ori_path.add_object(ori_l)
  #adv_path.add_object(adv_l)
  #adv_path.add_heading(adv_heading)
  #zipped = zip(ori_path.headings, adv_path.headings)

  #with open('headings.csv','w') as f:
  #  writer = csv.writer(f, delimiter='\t')
  #  writer.writerows(zipped)

  #difference_heading.append(adv_heading - float(heading))

  #with open('heading_difference.txt','w') as f:
  #  for heading in difference_heading:
  #      f.write("%f\n" % heading)

  #zip_obj = zip(ori_path.objects, adv_path.objects)
  #with open('objects.csv','w') as f:
  #  writer = csv.writer(f, delimiter='\t')
  #  writer.writerows(zip_obj)

  #difference_object.append(set(ori_l).symmetric_difference(set(adv_l)))

  #with open('object_difference.csv','w') as f:
  #  writer = csv.writer(f)
  #  writer.writerows(difference_object)

  #origin_images.append('./images/'+step_name)
  #if adv_found:
  #  adv_images.append('./images/adv_'+step_name)
  #else:
  #  adv_images.append('./images/'+step_name)
  #imgTogif(origin_images, adv_images)
  #if adv_found:
  #  return jsonify(image_ret=step_name, adv_image_ret='adv_'+step_name, img_gif_ret='./images/img_out.gif',adv_gif_ret='./images/adv_out.gif',new_h = new_heading)
  #else:
  #  return jsonify(image_ret=step_name, adv_image_ret=step_name, img_gif_ret='./images/img_out.gif',adv_gif_ret='./images/adv_out.gif',new_h = new_heading)

  origin_images.append('./images/'+step_name)
  adv_images.append('./images/adv_'+step_name)
  imgTogif(origin_images, adv_images)
  return jsonify(image_ret=step_name, adv_image_ret='adv_'+step_name, img_gif_ret='./images/img_out.gif',adv_gif_ret='./images/adv_out.gif',new_h = new_heading)

@app.route("/images/<path:path>")
def images(path):
    fullpath = "./images/"+path
    with open(fullpath, 'rb') as f:
        resp = flask.make_response(f.read())
    resp.content_type = "image/gif"
    return resp

if __name__=='__main__':
  app.run()
