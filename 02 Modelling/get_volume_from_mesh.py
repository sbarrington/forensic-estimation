import pickle
import trimesh
import math
import json
import os
import argparse

import json_skeleton

import pandas as pd
import numpy as np


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

def run_participant(image, results_file, lookup_table_location):
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
	scale_factor = known_ipd/ipd
	print(f'Using scale factor: {scale_factor} (model*sf = reality)')
	
	obj_input = results_file+'/'+image+'/posed.obj'
	mesh = trimesh.load(obj_input)
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
	
	participant_measurements['est_volume_m3'] = fitted_volume
	participant_measurements['est_mass_985kg_m3'] = mass_estimated_985
	
	return participant_measurements

def main():
	# Directory is jobname, which is 3_smplify_x_female. In here there will be 'results'. 
	# Inputs are thus: 
	# The 000.json file 

	parser = argparse.ArgumentParser()
	parser.add_argument('--results_file', type=str, required=True, help='Location of the photo files that each contain 000.pkl, alongside 000.json and 000.obj from "pose_model_for_simulation.py"')
	parser.add_argument('--csv_output_file', type=str, default="volume_results.csv", help='Where to store the final output volume CSV')
	parser.add_argument('--lookup_table_location', type=str, help='Location of participant lookup table')

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
		estimates = run_participant(image, results_file, lookup_table_location)
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
