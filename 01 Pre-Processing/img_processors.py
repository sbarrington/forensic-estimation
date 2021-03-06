import math
import cv2
import cvzone
import os
import shutil

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


def run_all_files(photos_location, ids, required_images, method='binary_mask', padding=False):
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
            if padding:
                img = pad_resize(img, 1024)

            if method == 'binary_mask':
                img_Out = create_binary_mask(img)
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/MASKS/binary_mask/binary_mask'+'_'+photos[i][:-3]+'png'

            elif method == 'bkg_removal':
                img_Out = remove_bkg(img)
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/MASKS/bkg_removal/bkg_removal'+'_'+photos[i][:-3]+'png'

            elif method == 'pad_resize_only':
                img_Out = img
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/MASKS/padded/padded'+'_'+photos[i][:-3]+'png'
        
            # SAVE STATEMENT
            #showimage(img_Out, figsize=[5,5]) # CHANGE THIS FOR ALL 
            cv2.imwrite(dest, img_Out)
        
        print(f'Completed mask generation files for ID {id_}')
    
    return None
 
def run_all_files_samefolder(photos_location, ids, required_images, method='binary_mask', padding=False):
    
    ''' As with run_all_files, 
    but writing out by ID folder 
    rather than separate test folders.
    '''

    for id_ in ids:
        
        # Get images that contain required_images in the name
        photos = os.listdir(photos_location+'/'+id_)
        photos = [x for x in photos if not x.startswith('.')]
        photos = sorted(photos)
        
        # Subset list for photo names containing those in required images
        photos = [i for i in photos if any(b in i for b in required_images)]
    
        for i in range(len(photos)): # CHANGE THIS FOR ALL
            source = photos_location+'/'+id_+'/'+photos[i]
    
            
            img = get_image(source)
            if padding:
                img = pad_resize(img, 1024)

            if method == 'binary_mask':
                img_Out = create_binary_mask(img)
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/'+id_+'/'+id_+'_binary_mask'+'_'+photos[i][4:-3]+'png'

            elif method == 'bkg_removal':
                img_Out = remove_bkg(img)
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/'+id_+'/'+id_+'_bkg_removal'+'_'+photos[i][4:-3]+'png'

            elif method == 'pad_resize_only':
                img_Out = img
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/'+id_+'/'+id_+'_padded'+'_'+photos[i][4:-3]+'png'
        
            # SAVE STATEMENT
            #showimage(img_Out, figsize=[5,5]) # CHANGE THIS FOR ALL 
            cv2.imwrite(dest, img_Out)
        
        print(f'Completed mask generation files for ID {id_}')
    
    return None

def create_binary_mask(img):
    img = remove_bkg(img, 0.70)
    kernel = np.ones((5, 5), np.uint8)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    Lower_hsv = np.array([0, 0, 250]) # Manually set to 250 to keep skin tones in
    Upper_hsv = np.array([172, 111, 255])

    # creating the mask by eroding,morphing,
    # dilating process
    Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
    Mask = cv2.erode(Mask, kernel, iterations=1)
    Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
    Mask = cv2.dilate(Mask, kernel, iterations=1)

    Mask = cv2.bitwise_not(Mask)

    return Mask


def pad_resize(img, pixels, print_progress=False, show_image=False):

    dims = img.shape

    pad = int((dims[0]-dims[1])/2)

    # Add horizontal padding
    img = cv2.copyMakeBorder(img, top=0, bottom=0, left=pad, right=pad, borderType=cv2.BORDER_CONSTANT)
    # Resize
    img = cv2.resize(img, (1024,1024), interpolation = cv2.INTER_AREA)

    if print_progress:
        print('Original Dimensions : ',dims)
        print('Resized Dimensions : ',img.shape)
    if show_image:
        showimage(img)
    
    return img

def pad_resize_gopro(img, pixels, print_progress=False, show_image=False):

    dims = img.shape

    pad = int((dims[1]-dims[0])/2) # Swapped top and bottom dims compared to the non-gopro image

    # Add VERTICAL padding
    img = cv2.copyMakeBorder(img, top=pad, bottom=pad, left=0, right=0, borderType=cv2.BORDER_CONSTANT)
    # Resize
    img = cv2.resize(img, (1024,1024), interpolation = cv2.INTER_AREA)

    if print_progress:
        print('Original Dimensions : ',dims)
        print('Resized Dimensions : ',img.shape)
    if show_image:
        showimage(img)
    
    return img


def run_all_files_images_folder(photos_location, output_location_padded, output_location_masks, ids, required_images, method='binary_mask', second_output_location=None, ext='jpg', padding_method='studio'):
    
    ''' As with run_all_files, 
    but writing out to an overall combined 'images' input file,
    as opposed to renaming files within given ID folder.
    '''

    for id_ in ids:
        
        # Get images that contain required_images in the name
        photos = os.listdir(photos_location+'/'+id_)
        photos = [x for x in photos if not x.startswith('.')]
        photos = sorted(photos)
        
        # Subset list for photo names containing those in required images
        photos = [i for i in photos if any(b in i for b in required_images)]
    
        for i in range(len(photos)): 
            source = photos_location+'/'+id_+'/'+photos[i]
    
            print(f'getting image from {source}')

            img = get_image(source)
            if padding_method=='studio':
                img_Out = pad_resize(img, 1024)
                dest = output_location_padded + 'padded_' + id_ + '_' + photos[i][4:-3]+ext

                print(f'Padded file being saved to {dest}')
                cv2.imwrite(dest, img_Out)
                if second_output_location is not None:
                    dest = second_output_location + 'padded_' + id_ + '_' + photos[i][4:-3]+ext
                    cv2.imwrite(dest, img_Out)

            elif padding_method=='gopro':
                img_Out = pad_resize_gopro(img, 1024)
                dest = output_location_padded + 'padded_' + id_ + '_' + photos[i][4:-3]+ext

                print(f'Padded go_pro file being saved to {dest}')
                cv2.imwrite(dest, img_Out)
                if second_output_location is not None:
                    dest = second_output_location + 'padded_' + id_ + '_' + photos[i][4:-3]+ext
                    cv2.imwrite(dest, img_Out)


            elif padding_method=='None':
                img_Out = img
                dest = output_location_padded + '_' + id_ + '_' + photos[i][4:-3]+ext

                print(f'Non-padded file being saved to {dest}')
                cv2.imwrite(dest, img_Out)
                if second_output_location is not None:
                    dest = second_output_location + '_' + id_ + '_' + photos[i][4:-3]+ext
                    cv2.imwrite(dest, img_Out)

            if method == 'binary_mask':
                img_Out = create_binary_mask(img_Out)
                dest = output_location_masks + 'padded_' + id_ + '_' + photos[i][4:-3]+ext

                print(f'Mask file being saved to {dest}')
                cv2.imwrite(dest, img_Out)

            elif method == 'bkg_removal':
                img_Out = remove_bkg(img)
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/'+id_+'/'+id_+'_bkg_removal'+'_'+photos[i][4:-3]+ext

            elif method == 'pad_resize_only':
                img_Out = img
                # TO WRITE TO SEPARATE FOLDER FOR SAMPLE ANALYSIS:
                dest = photos_location+'/'+id_+'/'+id_+'_padded'+'_'+photos[i][4:-3]+ext

            elif method == 'photoshop':
                img_Out = img
                if padding_method == 'gopro':
                    image_type = photos[i][4:-13]
                    dest = output_location_masks + image_type +  '/padded_' + id_ + '_' + photos[i][4:-3]+ext
                else:
                    dest =  output_location_masks + 'padded_' + id_ + '_' + photos[i][4:-3]+ext

                print(f'Photoshop input file being saved to {dest}')
                cv2.imwrite(dest, img_Out)
        
            # SAVE STATEMENT
            cv2.imwrite(dest, img_Out)
        
        print(f'Completed mask generation files for ID {id_}')
    
    return None


def rename_files(photos_location):    

    photos = os.listdir(photos_location)
    photos = [x for x in photos if not x.startswith('.')]
    photos = sorted(photos)

    for i in range(0, len(photos)):
        photo_path = photos_location+photos[i]
        photo_stem = os.path.dirname(photo_path)
        #shutil.move(photo_path, photo_stem+'/padded_'+photo)
        old_file = os.path.join(photos_location, photos[i])
        print({old_file})
        new_file = os.path.join(photos_location, photo_stem+"/padded_"+photos[i]) # Renames ID_image_DSC_XXXX.jpg to padded_ID_image_DSC_XXXX.jpg
        print(new_file)
        os.rename(old_file, new_file)

    return None
