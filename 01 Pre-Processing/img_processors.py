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

    return img_Out

def showimage(myimage):
    fig, ax = plt.subplots(figsize=[10,10])
    ax.imshow(cv2.cvtColor(myimage, cv2.COLOR_RGB2BGR))
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()
    
    return None

def apply_hsv_filter(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([0, 0, 120])
    upper_blue = np.array([180, 38, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    result = cv2.bitwise_and(img, img, mask=mask)
    b, g, r = cv2.split(result)  
    filter = g.copy()
        
    ret,mask = cv2.threshold(filter,0,255, 1)

    img[ mask == 0] = 255

    return img


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


def run_all_files(photos_location, ids, required_images, method='binary_mask'):
    for id_ in ids:
        
        # Get images that contain required_images in the name
        photos = os.listdir(photos_location+'/'+id_)
        photos = [x for x in photos if not x.startswith('.')]
        photos = sorted(photos)
        
        # Subset list for photo names containing those in required images
        photos = [i for i in photos if any(b in i for b in required_images)]
    
        for i in range(len(photos)): # CHANGE THIS FOR ALL
            source = photos_location+'/'+id_+'/'+photos[i]
            # TO WRITE INTO SAME FOLDER:
            #dest = photos_location+'/'+id_+'/'+'binary_mask'+'_'+photos[i]
            
            img = get_image(source)
            if method == 'binary_mask':
                img_Out = create_binary_mask(img)
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/MASKS/binary/binary_mask'+'_'+photos[i]
            elif method == 'bkg_removal':
                img_Out = remove_bkg(img)
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/MASKS/bkg_removal/bkg_removal'+'_'+photos[i]
        
            # SAVE STATEMENT
            #showimage(img_Out, figsize=[5,5]) # CHANGE THIS FOR ALL 
            cv2.imwrite(dest, img_Out)
        
        print(f'Completed binary mask generation files for ID {id_}')
    
    return None
 