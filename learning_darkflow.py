import os
import sys

import math
## Need Python version > 2.7
from collections import Counter
import cv2


imgcv = cv2.imread("./routes/ormeau_road/(step3)54.5876023,-5.9239714.jpeg")
## let's predict
results = tfnet.return_predict(imgcv)
