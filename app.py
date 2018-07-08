from flask import Flask, render_template
from flask import jsonify, request
import flask
from safety import check_safety_dflow
from safety import imgTogif
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

import urllib
count=0
origin_images=[]
adv_images=[]

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

  u = request.args.get('u', 0, type=str)


  https = request.args.get('https', 0, type=str)
  l_pano = request.args.get('l_pano', 0, type=str)
  fov = request.args.get('fov', 0, type=str)
  heading = request.args.get('heading', 0, type=str)
  pitch = request.args.get('pitch', 0, type=str)
  key = request.args.get('key', 0, type=str)

  global count

  print("check image")

  is_safe=check_safety_dflow(count, https, l_pano, float(fov), float(heading), float(pitch), key)
  count+=1

  step_name='step{0}.png'.format(count-1)
  if count<=10:
    step_name='step0{0}.png'.format(count-1)


  if is_safe:
    origin_images.append('./images/'+step_name)
    imgTogif(origin_images,adv_images)
    return jsonify(image_ret=step_name, adv_image_ret='', img_gif_ret='./images/img_out.gif')
  else:
    origin_images.append('./images/'+step_name)
    adv_images.append('./images/adv-'+step_name)
    imgTogif(origin_images, adv_images)
    return jsonify(image_ret=step_name, adv_image_ret='adv-'+step_name, img_gif_ret='./images/img_out.gif',adv_gif_ret='./images/adv_out.gif')


@app.route("/images/<path:path>")
def images(path):
    fullpath = "./images/"+path
    with open(fullpath, 'rb') as f:
        resp = flask.make_response(f.read())
    resp.content_type = "image/gif"
    return resp

if __name__=='__main__':
  app.run()
