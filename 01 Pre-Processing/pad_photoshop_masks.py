# Packages 
import os
import yaml
import cv2
import cvzone
import numpy as np

import img_processors as proc
import data_processors as dp

from cvzone.SelfiSegmentationModule import SelfiSegmentation

def get_config_inputs(yaml_file):

    with open(yaml_file, 'r') as file:
        inputs = yaml.load(file, Loader=yaml.FullLoader)

    return inputs

def pad_clean_photoshop_masks(photoshop_output_location, completed_mask_output_location, padding_method):
    photos = os.listdir(photoshop_output_location)
    photos = [x for x in photos if not x.startswith('.')]
    photos = sorted(photos)

    for i in range(len(photos)): 
        source = photoshop_output_location+photos[i]

        print(f'getting image from {source}')
        
        # PADDING
        img = proc.get_image(source)
        if padding_method=='studio':
            img_Out = proc.pad_resize(img, 1024)
            dest = completed_mask_output_location + photos[i]

            print(f'Padded file being saved to {dest}')


        elif padding_method=='gopro':
            img_Out = proc.pad_resize_gopro(img, 1024)
            dest = completed_mask_output_location + photos[i]

            print(f'Padded go_pro file being saved to {dest}')
        
        # CLEANING (grayscale -> binary)
        grayImage = cv2.cvtColor(img_Out, cv2.COLOR_BGR2GRAY)
        (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
        cv2.imwrite(dest, blackAndWhiteImage)
        # Check:
        if len(np.unique(blackAndWhiteImage)) > 2:
            print('Warning! Binary mask still contains grey')
            
    return None

def main():

	# Calibration & args
	yaml_config = '../XX Data/config.yaml'
	inputs = get_config_inputs(yaml_config)

	photoshop_output_location = inputs['output_location_photoshop']
	completed_mask_output_location = inputs['output_location_masks']
	padding_method = inputs['padding_method']

	# Calibration & args
	yaml_config = '../XX Data/config.yaml'
	inputs = get_config_inputs(yaml_config)

	pad_clean_photoshop_masks(photoshop_output_location, completed_mask_output_location, padding_method)

	return None

if __name__ == "__main__":
	main()