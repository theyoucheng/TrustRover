from flask import Flask, render_template
from flask import jsonify, request, send_file
from PIL import Image
import flask
import Simulator

app=Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
  return render_template('homepage.html')

@app.route('/get_route')
def get_route():
    route = request.args.get('route', 0, type=str)
    yolo = request.args.get('yolo', 0, type=str)
    Simulator.run(route, yolo)
    
    return jsonify(img_gif_ret='./completed_routes/'+route+'/journey.gif')

@app.route("/completed_routes/<route>/<gif>")
def images(route, gif):
    fullpath = "./completed_routes/"+route+'/'+gifgit add
    with open(fullpath, 'rb') as f:
        resp = flask.make_response(f.read())
    resp.content_type = "image/gif"
    return resp


if __name__=='__main__':
  app.run(host='0.0.0.0')

