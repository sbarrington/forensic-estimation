import pickle
import trimesh
import math
import json

import json_skeleton

import pandas as pd
from cmd_parser import parse_config
import openmesh as om
import numpy as np

def get_participant_measurements(participant_id, lookup_table_location):
	# Ingest lookup table
	lookup_table = pd.read_csv(lookup_table_location)
	lookup_table = 



def main():
	# Directory is jobname, which is 3_smplify_x_female. In here there will be 'results'. 
	# Inputs are thus: 
	# The 000.json file 

	parser = argparse.ArgumentParser()
    parser.add_argument('--posed_json', type=str, required=True,
                        help='Location of the 000.json posed skeleton output from "pose_model_for_simulation.py"')
    parser.add_argument('--posed_obj', type=str, required=True,
                        help='Location of the 000.obj posed skeleton output from "pose_model_for_simulation.py"')
    parser.add_argument('--csv_output_file', type=str,
                        default="volume_results.csv", help='Where to store the final output volume CSV')
    parser.add_argument('--lookup_table_location', type=str,
                        help='Location of participant lookup table')
    parser.add_argument('--participant_id', type=str,
                        help='Participant ID for the single given image')

    args, remaining = parser.parse_known_args()
    print(args)

    posed_json_input = args.posed_json
    posed_obj_input = args.posed_obj
    output_csv = args.csv_output_file
    lookup_table_location = args.lookup_table_location
    participant_id = args.participant_id

	posed = json_skeleton.JsonSkeleton(posed_json_input)
	ipd = posed.get_IPD()*100 # Convert to centimeters

	participant_id = 

	participant_measurements = get_participant_measurements(participant_id,lookup_table_location)
	known_ipd = participant_measurements['ipd_cm']
	print(f'Measured IPD = {known_ipd}cm')
	scale_factor = known_ipd/ipd
	print(f'Using scale factor: {scale_factor} (model*sf = reality)')

	mesh = trimesh.load(posed_json_input)
	print(f'Unfitted volume is: {mesh.volume}')
	fitted_mesh = mesh.apply_transform(trimesh.transformations.scale_matrix(scale_factor))

	fitted_volume = fitted_mesh.volume

	print("fitted volume is: " + str(fitted_volume))

	#0.07205m^3 = Xkg. Denisty = mass/volume. KNOWN MASS - 75
	known_mass = 75
	mass = 985*fitted_volume
	print('   ')
	print('---WEIGHT ESTIMATION RESULTS---')
	print(f'Mass estimated is {mass}kg')
	print(f'Known mass is {known_mass}kg')


if __name__ == "__main__":
	main()