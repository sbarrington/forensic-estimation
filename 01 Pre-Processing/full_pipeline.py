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

def main():

	### [X] STEP 0: Tidy raw camera files and create participant folders- see data_processing notebook ###

	### [X] STEP 1: Calibrate ###

	# Calibration & args
	yaml_config = '../XX Data/config.yaml'
	inputs = get_config_inputs(yaml_config)

	photos_location = inputs['photos_location']
	n = inputs['n']
	output_location_openpose = inputs['output_location_openpose']
	output_location_masks = inputs['output_location_masks']
	output_location_smplifyx = inputs['output_location_smplifyx']
	padding_method = inputs['padding_method']

	required_images = inputs['required_images']

	### [X] STEP 2: Generate padded images and binary masks
	ids = dp.generate_ids(n)
	# Uncomment for testing only 
	#ids = ['003', '014', '050']

	### STEP 2.5: When script fails at 35th element for unknown reason:
	#ids = ids[35:] # Takes you from ID036 onwards

	proc.run_all_files_images_folder(photos_location, output_location_openpose, output_location_masks, ids, required_images, method='binary_mask', second_output_location=output_location_smplifyx, ext='png', padding_method=padding_method)


	### STEP X: 

if __name__ == "__main__":
	main()