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

	required_images = inputs['required_images']

	### [X] STEP 2: Generate padded images and binary masks
	ids = dp.generate_ids(n)
	# Uncomment for testing only 
	#ids = ['003', '014', '050']

	### STEP 2.5: When script fails at 35th element for unknown reason:
	#ids = ids[35:] # Takes you from ID036 onwards

	proc.run_all_files_images_folder(photos_location, output_location_openpose, output_location_masks, ids, required_images, method='binary_mask', padding=True, second_output_location=output_location_smplifyx, ext='png')

	### [X] STEP XX: Create Gender, height, weight, IPD lookup by running the separate script 
	## in the 00 directory - store in 3_smplify-x/smplify-x_input folder. 

	### [X] GDRIVE - STEP 3: Copy the output_location_openpose & output_location_smplifyx into google drive folders with same names ###

	### [X] COLAB - STEP 4: RUN OPENPOSE (colab notebook) ###

	### [x] GDRIVE - download openpose results from 3_smplify-x/smplify-x_input/keypoints folder 
	# Unzip this 'keypoints' file in the 3_smplify-x/smplify-x_input local directory

	### [in prog] GDRIVE/LOCAL - STEP 5: zip & transfer whole local 3_smplify-x to VM via SSH ###

	### SEPARATE GENDERS go from 3_smplify-x -> 3_smplify-x_female & male
	# On VM, run: bash separate_genders.py --jobname 3_smplify-x --lookup_location 3_smplify-x/smplify-x_input/participant_lookup.csv --gender_directory_location current

	# RUN 2X JOBS, ONE PER GENDER
	# RUN 2X 'GET VOLUMES', ONE PER GENDER (I NEED TO FINISH THE VOLUME EXTRACTION TO CSV)
		

	### [] VM - STEP X: RUN SMPLIFY-X CODE for first gender, repeat for second gender###
	# 	conda activate hw_render
	#	bash fit_images_sil.sh ~/3_smplify-x_male male results 3000 0.01 
	#	bash fit_images_sil.sh ~/3_smplify-x_female female results 3000 0.01 

	### [] VM - STEP X: RUN VOLUME SIMULATION ###
	# 	bash get_volumes.sh ~/3_smplify-x_female female 3_smplify-x/smplify-x_input/participant_lookup.csv
	#	bash get_volumes.sh ~/3_smplify-x_male male 3_smplify-x/smplify-x_input/participant_lookup.csv

	### STEP ?X: TRANSFER RESULTS TO LOCAL ### [SSH + ZIP FILE?]
	# Zip results for browsing locally: 
	# zip -r results_female.zip 3_smplify-x_female/results/
	# zip -r results_male.zip 3_smplify-x_male/results/


	### STEP X: 

if __name__ == "__main__":
	main()