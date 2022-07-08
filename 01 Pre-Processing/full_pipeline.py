# Packages 
import os
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

	### [X] OPTIONAL: Create Gender lookup by running the separate script in this directory ###

	### [X] STEP 1: Calibrate ###

	# Calibration & args
	yaml_config = '../XX Data/config.yaml'
    inputs = get_config_inputs(yaml_config)

	photos_location = inputs['photos_location']
	n = inputs['n']
	output_location_openpose = inputs['output_location_openpose']
	output_location_masks = inputs['output_location_masks']
	output_location_smplifyx = inputs['output_location_smplifyx']

	required_images = inputs['required_images']

	### [X] STEP 2: Generate padded images and binary masks
	ids = dp.generate_ids(n)
	#ids = ['003', '014', '050']

	### STEP 2.5: When script fails at 35th element for unknown reason:
	#ids = ids[35:] # Takes you from ID036 onwards

	proc.run_all_files_images_folder(photos_location, output_location_openpose, output_location_masks, ids, required_images, method='binary_mask', padding=True, second_output_location=output_location_smplifyx)

	### [X] GDRIVE - STEP 3: Copy the output_location_openpose & output_location_smplifyx into google drive folders with same names ###

	### [X] COLAB - STEP 4: RUN OPENPOSE (colab notebook) ###

	### [X] GDRIVE/LOCAL - STEP 5: TRANSFER SMPLIFY-X INPUTS *AND GENDER LOOKUP* TO VM ### [SSH + ZIP FILE?]

	### [] VM - STEP X: RUN SMPLIFY-X CODE ###
	# BASH/PYTHON SCRIPT:
	# 	Feed in gender array (from a CSV file arg?) 
	# 	conda activate hw_render
	#	bash fit_images_sil.sh INPUTFOLDER <GENDER> results 3000 0.01

	### [] VM - STEP X: RUN VOLUME SIMULATION ###
	#	run via python: smplify-x-sil/smplifyx/pose_model_for_simulation.py on pckled result

	### STEP ?X: TRANSFER RESULTS TO LOCAL ### [SSH + ZIP FILE?]

	### STEP X: 

if __name__ == "__main__":
	main()