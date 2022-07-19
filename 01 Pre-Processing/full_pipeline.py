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

	# Calibration & args
	yaml_config = '../XX Data/config.yaml'
	inputs = get_config_inputs(yaml_config)

	photos_location = inputs['photos_location']
	n = inputs['n']
	output_location_openpose = inputs['output_location_openpose']
	output_location_masks = inputs['output_location_masks']
	output_location_smplifyx = inputs['output_location_smplifyx']
	padding_method = inputs['padding_method']
	method = inputs['method']

	required_images = inputs['required_images']

	if method == 'photoshop':
		output_location_masks = inputs['input_location_photoshop']

	ids = dp.generate_ids(n)
	
	# Uncomment for testing only 
	#ids = ['003', '014', '050']

	### If script fails at 35th element for unknown reason:
	#ids = ids[35:] # Takes you from ID036 onwards

	proc.run_all_files_images_folder(photos_location, output_location_openpose, output_location_masks, ids, required_images, method=method, second_output_location=output_location_smplifyx, ext='png', padding_method=padding_method)


	### STEP X: 

if __name__ == "__main__":
	main()