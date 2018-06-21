from flask import Flask, render_template
from flask import jsonify, request
import flask
from safety import check_safety
from safety import check_robust_safety
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

import urllib
count=0

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

  is_safe=check_robust_safety(count, https, l_pano, float(fov), float(heading), float(pitch), key)
  count+=1

  step_name='step{0}.png'.format(count-1)
  if count<=10:
    step_name='step0{0}.png'.format(count-1)

  if is_safe:
    return jsonify(image_ret=step_name.format(count-1), adv_image_ret='')
  else:
    return jsonify(image_ret=step_name, adv_image_ret='adv-'+step_name)


@app.route("/images/<path:path>")
def images(path):
    fullpath = "./images/"+path
    resp = flask.make_response(open(fullpath).read())
    resp.content_type = "image/jpeg"
    return resp

if __name__=='__main__':
  app.run()
