import pickle
import trimesh
import math
import json
import os
import argparse

import json_skeleton

import pandas as pd
import numpy as np

from sympy import Plane, Point3D

def get_obj_keypoints(obj_file):
    points = {}
    f = open(obj_file, "r")
    linenum = 1
    for line in f:
        if line.startswith("v "):
            coords = line.split(" ")
            x = float(coords[1])
            y = float(coords[2])
            z = float(coords[3])
            points[linenum] = (x, y, z)

        linenum += 1
    
    return {"top_head": points[9004], "r_toe": points[8489], "r_heel": points[8717], "l_toe": points[5795]}

def height_from_keypoints(keypoints):
    top_head = Point3D(keypoints["top_head"])
    r_toe = Point3D(keypoints["r_toe"])
    r_heel = Point3D(keypoints["r_heel"])
    l_toe = Point3D(keypoints["l_toe"])

    ground_plane = Plane(r_toe, r_heel, l_toe) 
    print(ground_plane)

    return ground_plane.distance(top_head).evalf()

def get_participant_measurements(image, lookup_table_location):
	# Ingest lookup table
	lookup_table = pd.read_csv(lookup_table_location, index_col=0)
	photo = os.path.basename(image)
	participant_id = get_participant_id(image)
	print(f'Looking up {photo}')
	participant_measurements={}
	participant_measurements['id'] = str(participant_id)
	participant_measurements['image'] = str(image)+'.png'
	for column in lookup_table.columns:
		participant_measurements[column] = lookup_table.loc[photo+'.png', column]
	
	return participant_measurements


def get_participant_id(file_or_folder_name):
	return ''.join(c for c in file_or_folder_name if c.isdigit())[:3]

def get_height(obj_input, scale_factor, participant_measurements):
	keypoints = get_obj_keypoints(obj_input) 
	fitted_height_unscaled = height_from_keypoints(keypoints)*100 

	fitted_height = fitted_height_unscaled*scale_factor

	print("fitted height is: " + str(fitted_height))

	known_height = participant_measurements['height_cm']
	print('   ')
	print('---HEIGHT ESTIMATION RESULTS---')
	print(f'Height estimated is {fitted_height}cm')
	print(f'Known height is {known_height}cm')

	return fitted_height

def run_participant(image, results_file, lookup_table_location):
	print(image)
	participant_id = get_participant_id(image)
	posed_json_input = results_file+'/'+image+'/posed.json'
	print(f'POSED JSON INPUT: {posed_json_input}')
	posed = json_skeleton.JsonSkeleton(posed_json_input)
	ipd = posed.get_IPD()*100 # Convert to centimeters
	
	participant_measurements = get_participant_measurements(image,lookup_table_location)
	known_ipd = float(participant_measurements['ipd_cm'])

	scale_factor = known_ipd/ipd
	
	print(f'Using scale factor: {scale_factor} (model*sf = reality)')
	
	obj_input = results_file+'/'+image+'/posed.obj'
	mesh = trimesh.load(obj_input)
	
	fitted_height = get_height(obj_input, scale_factor, participant_measurements)
	participant_measurements['est_height_cm'] = fitted_height
	
	return participant_measurements

def get_user_specific_ipd_correction(estimates, image, lookup_table_location):
	estimated_neutral_height = estimates['est_height_cm']
	actual_height = estimates['height_cm']
	model_to_actual_height_adjustment = actual_height/estimated_neutral_height
	adjusted_ipd = estimates['ipd_cm']*model_to_actual_height_adjustment

	# OVERWRITE: ADJUST IPD BY U.S.A GENDER AVERAGE INSTEAD OF HEIGHT SPECIFIC CONVERSION
	gender = get_participant_gender(image, lookup_table_location)

	if gender == 'male': 
 			adjusted_ipd = 6.40
 			print(f'Using MALE adjusted IPD of {adjusted_ipd}cm')
 	elif gender == 'female':
 			adjusted_ipd = 6.17
 			print(f'Using FEMALE adjusted IPD of {adjusted_ipd}cm')

	return adjusted_ipd

def get_participant_gender(image, lookup_table_location):
	# Ingest lookup table
	lookup_table = pd.read_csv(lookup_table_location, index_col=0)
	photo = os.path.basename(image)
	participant_id = get_participant_id(image)
	print(f'Looking up {photo}')
	gender = lookup_table.loc[photo+'.png', 'gender_identity']
	
	return gender

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--jobname', type=str, required=True)

	args = parser.parse_args()
	print(args)

	jobname = args.jobname # WITHOUT A SLASH AT END
	results_file = jobname+'/results/results' # NO SLASH AT END, STUDIO IMAGES ONLY!
	output_csv = jobname+'/smplify-x_input/adjusted_ipd_lookup.csv'
	jobname_without_gender = '_'.join(jobname.split('_')[:-1])
	lookup_table_location = jobname_without_gender+'/smplify-x_input/participant_lookup.csv'

	images = [x for x in os.listdir(results_file) if not x.startswith('.')]

	columns_from_lookup = pd.read_csv(lookup_table_location).columns
	ipd_table = pd.DataFrame(columns=columns_from_lookup)

	for image in images:
		print(f'Running estimates for image: {image}') 
		if 'rotation_0_' in image:
			participant_id = get_participant_id(image)
			ipd_estimates = run_participant(image, results_file, lookup_table_location)
			adjusted_ipd = get_user_specific_ipd_correction(ipd_estimates, image, lookup_table_location)

			ipd_estimates['adjusted_ipd'] = adjusted_ipd
			ipd_table = ipd_table.append(ipd_estimates, ignore_index=True)

		else:
			continue

	print(ipd_table)
	ipd_lookup = ipd_table[['id', 'adjusted_ipd']].drop_duplicates()
	ipd_lookup['adjusted_ipd'] = ipd_lookup['adjusted_ipd'].astype(float)
	ipd_lookup.to_csv(output_csv, header=True, index=False)

	return None


if __name__ == "__main__":
	main()
