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


