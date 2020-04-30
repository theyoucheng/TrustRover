from flask import Flask, render_template
from flask import jsonify, request, send_file
import flask
import Simulator

app=Flask(__name__)

# gets the home page of the application
@app.route('/', methods=['GET', 'POST'])
def index():
  return render_template('homepage.html')

# api called to start simulator and return the gifs location on server
@app.route('/get_route')
def get_route():
    route = request.args.get('route', 0, type=str)
    yolo = request.args.get('yolo', 0, type=str)
    Simulator.run(route, yolo)
    
    return jsonify(img_gif_ret='./completed_routes/'+route+'/journey.gif')

# api called by image tag source attribute to gather completed gif from server
@app.route("/completed_routes/<route>/<gif>")
def images(route, gif):
    fullpath = "./completed_routes/"+route+'/'+gif
    with open(fullpath, 'rb') as f:
        resp = flask.make_response(f.read())
    resp.content_type = "image/gif"
    return resp

# needed for running script as flask web server
if __name__=='__main__':
  app.run(host='0.0.0.0')

