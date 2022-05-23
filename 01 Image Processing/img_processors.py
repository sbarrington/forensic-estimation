import math
import cv2
import cvzone

from cvzone.SelfiSegmentationModule import SelfiSegmentation

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

''' 
IMAGE PROCESSING HELPER FUNCTIONS

Author: Sarah Barrington
Date: 18TH May 2022

'''

def get_image(myimage_path):
    img = cv2.imread(myimage_path)
    
    return img

def remove_bkg(img, threshold=0.7):
    segmentor = SelfiSegmentation()
    img_Out = segmentor.removeBG(img, (255,255,255), threshold=threshold)

    fig, ax = plt.subplots(figsize=[10,10])
    ax.imshow(cv2.cvtColor(img_Out, cv2.COLOR_RGB2BGR))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()
    
    return None

def showimage(myimage):
    fig, ax = plt.subplots(figsize=[10,10])
    ax.imshow(cv2.cvtColor(myimage, cv2.COLOR_RGB2BGR))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()
    
    return None


def create_catch_trial(img, threshold=0.7):
    segmentor = SelfiSegmentation()
    img_Out = segmentor.removeBG(img, (255,255,255), threshold=threshold)
    
    height = img_Out.shape[0]
    width = img_Out.shape[1]
    
    fig, ax = plt.subplots(figsize=[10,10])
    
    cv2.line(img_Out, (1000,1350), (1000, 4500), (0,0,255), 12)
    cv2.line(img_Out, (1000,1350), (2000, 1350), (0,0,255), 12)
    cv2.line(img_Out, (1000,4500), (1690, 4500), (0,0,255), 12)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img_Out, '157.6cm (5 ft 2 in)', (100,1200), font, 5, (0, 0, 255), 5, cv2.LINE_AA)
    
    ax.imshow(cv2.cvtColor(img_Out, cv2.COLOR_RGB2BGR))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()
    
    return None
 