# TrustRover

# Trust Google Account
   account: trustrover@gmail.com
   password : CSC3002Project
   API KEY: AIzaSyBX_EJ7eVl--YFwkFzIB1wegoz4e-9q_78


Step 1
download conda python package and environment manager
https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html


Step 2
use conda to create an environment
https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf

Step 3
install the following packages into your newly created conda environment:
 -- Python3
 -- cython
 -- tensorflow 1.15(https://anaconda.org/conda-forge/tensorflow)
 -- numpy
 -- cv2
 -- flask
 -- imageio
 -- shapely
 -- unittest

this can be done using the conda package manager
***ensure that you are downloing these using conda install***
**ensure tensorflow is version 1.15**
** For example **
** command to install tensorflow "conda install -c conda-forge tensorflow==1.15" **
** command to download cython "conda install cython" **

Step 4
download(or clone) darkflow and install within the TrustRover Directory
https://github.com/thtrieu/darkflow

 step 4 a)
    within the cloned dir"./darkflow" run the command "python3 setup.py build_ext --inplace"
 step 4 b)
    move the "darkflow" dir that is within the outter "darkflow" dir, "./darkflow/darkflow" into the root dir of your project ."/"
 step 4 c)
    you can remove or rename the original "darkflow" folder. suggestion: change to "darkflow_install_folder"


step 5
download the yolo.weights from the project google drive
https://drive.google.com/drive/u/0/folders/1jpZVz67p-RN99JaFpy4hM7wkftbyaR-m

 -- add all the "*.weights" files into the ./cfg/bin folder
 -- add the "*.cfg" into the ./cfg folder
 -- the "labels.txt" file goes in the root directory of the project "./"


step 8
activate the conda env that you been created for this project

step 9
while in the specified env, navigate to the trustrover root directory "./"

step 10
run the command "python app.py"

step 11
in your browser type in the url "localhost:5000"

step 12
trustrover is now available to use. Simply select the route you wish to view and the object detection model you wish to use.

The program will then create gifs that show the route via streetview images with an overlaying boundary box and car status. 

# # Completed simulation

in the "completed_simulations" folder there can be found the completed routes, 
for each of the route and each yolo model



 







