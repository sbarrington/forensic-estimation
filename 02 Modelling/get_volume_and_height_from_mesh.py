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

def get_volume(mesh, scale_factor, participant_measurements):
	print(f'Unfitted volume is: {mesh.volume}')
	fitted_mesh = mesh.apply_transform(trimesh.transformations.scale_matrix(scale_factor))

	fitted_volume = fitted_mesh.volume

	print("fitted volume is: " + str(fitted_volume))

	#0.07205m^3 = Xkg. Denisty = mass/volume. KNOWN MASS - 75
	known_mass = participant_measurements['weight_kg']
	mass_estimated_985 = 985*fitted_volume
	print('   ')
	print('---WEIGHT ESTIMATION RESULTS---')
	print(f'Mass estimated using 985kg/m^3 is {mass_estimated_985}kg')
	print(f'Known mass is {known_mass}kg')

	return fitted_volume, mass_estimated_985

def run_participant(image, results_file, lookup_table_location, gender):
	print(image)
	participant_id = get_participant_id(image)
	posed_json_input = results_file+'/'+image+'/posed.json'
	print(f'POSED JSON INPUT: {posed_json_input}')
	posed = json_skeleton.JsonSkeleton(posed_json_input)
	ipd = posed.get_IPD()*100 # Convert to centimeters
	
	participant_measurements = get_participant_measurements(image,lookup_table_location)
	known_ipd = participant_measurements['ipd_cm']
	print(f'Measured IPD = {known_ipd}cm')
	print(f'Model IPD = {ipd}cm')
	# UPDATE: 
	# ADD IN ADDITIONAL SCALING FOR MEASUREMENT CORRECTION
        print(f'Original IPD was {known_ipd}')
	known_ipd = known_ipd * ((((6/4.9)-1)/2)+1) # To try and equalise means 	# USE GENDER AVERAGES
	# FOR USING POPULATION AVERAGES
	#if gender == 'male': 
	#	known_ipd = 6.40
	#elif gender == 'female':
	#	known_ipd = 6.17
	print(f'Using ipd of = {known_ipd}')
	# Continue
	scale_factor = known_ipd/ipd
	
	print(f'Using scale factor: {scale_factor} (model*sf = reality)')
	
	obj_input = results_file+'/'+image+'/posed.obj'
	mesh = trimesh.load(obj_input)

	fitted_volume, mass_estimated_985 = get_volume(mesh, scale_factor, participant_measurements)	
	participant_measurements['est_volume_m3'] = fitted_volume
	participant_measurements['est_mass_985kg_m3'] = mass_estimated_985
	
	fitted_height = get_height(obj_input, scale_factor, participant_measurements)
	participant_measurements['est_height_cm'] = fitted_height
	
	return participant_measurements

def main():
	# Directory is jobname, which is 3_smplify_x_female. In here there will be 'results'. 
	# Inputs are thus: 
	# The 000.json file 

	parser = argparse.ArgumentParser()
	parser.add_argument('--results_file', type=str, required=True, help='Location of the photo files that each contain 000.pkl, alongside 000.json and 000.obj from "pose_model_for_simulation.py"')
	parser.add_argument('--csv_output_file', type=str, default="volume_results.csv", help='Where to store the final output volume CSV')
	parser.add_argument('--lookup_table_location', type=str, help='Location of participant lookup table')
	parser.add_argument('--gender', type=str)

	args = parser.parse_args()
	print(args)

	results_file = args.results_file
	output_csv = args.csv_output_file
	lookup_table_location = args.lookup_table_location

	images = [x for x in os.listdir(results_file) if not x.startswith('.')]

	columns_from_lookup = pd.read_csv(lookup_table_location).columns
	#columns_from_lookup = columns_from_lookup.append("image")
	results_table = pd.DataFrame(columns=columns_from_lookup)

	for image in images:
		print(f'Running estimates for image: {image}')
		estimates = run_participant(image, results_file, lookup_table_location, gender)
		results_table = results_table.append(estimates, ignore_index=True)
	results_table.index=results_table['id']
	results_table = results_table.drop(['Unnamed: 0', 'id'], axis=1)
	results_table = results_table.sort_index()
	first_column = results_table.pop('image')
	results_table.insert(0, 'image', first_column)
	results_table.to_csv(output_csv, header=True)

	return None


if __name__ == "__main__":
	main()
