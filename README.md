# TrustRover

## To run
**  python app.py

Type http://localhost:5000/ in your favourite and choose the route you want to play,
simply filling the start and destination and clicking the button.
A GooglAPI key is hard coded in the application.
Google sets a threshold for the number of images that can be downloaded by using a key
per day. Please do not go beyond that.

The object detection and detection is implemented in safety.py. It uses darknet 
(https://github.com/pjreddie/darknet). *TODO Replace darknet with darkflow 
https://github.com/thtrieu/darkflow.


Step 1
download conda python package and environment manager
https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html


Step 2
use conda to create an environment
https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf

Step 3
install the following packages into your newly created conda environment:
Python3, cython, tensorflow 1.15(https://anaconda.org/conda-forge/tensorflow), numpy, opencv 3, flask.
this can be done using the conda package manager
***ensure that you are downloing these using conda install***
**ensure tensorflow is 1.15**
** command to install tensorflow "conda install -c conda-forge tensorflow==1.15" **
** command to download cython "conda install cython" **

Step 4
download darkflow and install within the TrustRover Directory
https://github.com/thtrieu/darkflow

 step 4 a)
    within the cloned dir("darkflow" run the command "python3 setup.py build_ext --inplace")
step 4 b)
    move the "darkflow" dir that is within the outter "darkflow" dir into the root dir of your project


step 5
download the yolo.weights and add it into the cfg folder
http://pjreddie.com/media/files/yolo.weights

step 6
ensure that you have a google cloud platform api key created for use with the street view apis. this is done through the google cloud platform portal.

step 7
ensure that the following apis are enabled in your google cloud platform
Directions API
Distance Matrix API
Maps JavaScript API
Street View Static API

step 8
activate the conda env that you been created for this project

step 9
while in the specified env, navigate to the trustrover directory

step 10
run the command "python app.py"

step 11
in your browser type in the url "localhost:5000"

step 12
trustrover is now available to use. To use trust rover, simply add in the starting point of the route and the destination and the api key is different to the one hard coded in the file.

The program will then created gifs that show the routes via streetview with an overlaying boundary box, any object that is detected in that box is identified. 

there is also a map at the bottom of the webpage that shows the route tyou have selected on google maps.
 







