import pathlib
import json
import os
import math
import random
import time

import numpy as np
import cv2


numLevels = 256
numChannels = 3

dim = int(math.sqrt(pow(numLevels, numChannels))); 
curX = curY = 0

img = np.zeros((dim,dim, 3), np.uint8)
for rVal in range(0,numLevels):
  for gVal in range(0,numLevels):
      for bVal in range(0,numLevels):
        img[curX][curY] = [rVal, gVal, bVal]
        curX += 1
        if (curX >= dim):
            curX = 0;
            curY += 1      

cv2.imwrite("test.jpg", img)