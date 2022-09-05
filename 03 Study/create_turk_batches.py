import pickle
import math
import os
import argparse
import random
import shutil

import pandas as pd
import numpy as np

from PIL import Image

def get_participant_id(file_or_folder_name):
		return ''.join(c for c in file_or_folder_name if c.isdigit())[:3]

def extract_poses_and_types(image):
    return image[11:-13]

def create_batches(jpg_folder, n, participant_lookups_location, n_images=None):
	for folder in [x for x in os.listdir(jpg_folder) if not x.startswith('.') and not 'batch' in x]:
		folder_path = jpg_folder+'/'+folder
		print(f'FOLDER PATH": {folder_path}')
		# search for image: access ID folder, and look for image containing pose name
		batches_output = jpg_folder+f'/turk_batches_{folder}'
		if not os.path.exists(batches_output):
			os.mkdir(batches_output)
			# Create n folders ready to house batches - one per photogrammetrist
			for i in range(1, n+1):
				os.mkdir(batches_output+'/batch_'+f'{i}')

		if 'gopro' in folder:
			lookup = pd.read_csv(participant_lookups_location+'/gopro_participant_lookup.csv')
		else:
			lookup = pd.read_csv(participant_lookups_location+'/participant_lookup.csv')
		
		# Clean participant table
		lookup = lookup.rename(columns={'Unnamed: 0': 'image'})
		lookup['id'] = [get_participant_id(image) for image in lookup['image']]
		lookup.index = lookup['id']

		# Extract poses
		lookup['pose'] = [extract_poses_and_types(image) for image in lookup['image']]
		
		# Create partitions - x IDs per partition
		ids = lookup['id'].unique()

		# Generate random selections per partition 
		counter = 1
		
		for batch in range(0, n):
			batch_ids = ids
			n_ids = len(ids)
			poses = lookup['pose'].unique()
			## START HERE! subset poses for just the desired ones e.g. 2 action, 2 neutral etc . 
			#if not go pro:
			#  poses = desired poses 
			if 'gopro' not in folder:
				required_images = ['rotation_0', 'rotation_90', 'rotation_270', 'pose_squat', 'pose_fall']
				poses = [i for i in poses if any(b in i for b in required_images)]

			# Default value of n_images is 5
			n_images = n_ids
		
			for i in range(0, len(batch_ids)):
				if i == 0:
					pose_iterator = i + counter
				if pose_iterator == len(poses):
					pose_iterator = pose_iterator - len(poses)
				print(f'i: {i}')
				print(f'Pose iterator: {pose_iterator}')
				print(f'batch IDs: {batch_ids}')
				id_images = [x for x in os.listdir(folder_path) if x.startswith(f'{batch_ids[i]}_')]
				print(f'id_images: {id_images}')
				required_image_name = [x for x in id_images if poses[pose_iterator] in x]
				required_image_path = folder_path+'/'+required_image_name[0]
				print(f'Required image name {i} for batch {counter}: {required_image_name}')
				
				source = required_image_path
				destination = batches_output+'/batch_'+f'{counter}'+'/'+required_image_name[0]
				
				#print(id_images)
				shutil.copyfile(source, destination)

				pose_iterator = pose_iterator + 1

				# Write them out to the right files 

				# save to folder
			
			counter = counter + 1

	return None


def create_mixed_batch(jpg_folder, n, participant_lookups_location, n_images=None):
	for folder in [x for x in os.listdir(jpg_folder) if not x.startswith('.') and not 'batch' in x]:
		folder_path = jpg_folder+'/'+folder
		print(f'FOLDER PATH": {folder_path}')
		# search for image: access ID folder, and look for image containing pose name
		batches_output = jpg_folder+f'/mixed_batch'
		if not os.path.exists(batches_output):
			os.mkdir(batches_output)
			# Create n folders ready to house batches - one per photogrammetrist
			for i in range(1, n+1):
				os.mkdir(batches_output+'/batch_'+f'{i}')

		if 'gopro' in folder:
			lookup = pd.read_csv(participant_lookups_location+'/gopro_participant_lookup.csv')
		else:
			lookup = pd.read_csv(participant_lookups_location+'/participant_lookup.csv')
		
		# Clean participant table
		lookup = lookup.rename(columns={'Unnamed: 0': 'image'})
		lookup['id'] = [get_participant_id(image) for image in lookup['image']]
		lookup.index = lookup['id']

		# Extract poses
		lookup['pose'] = [extract_poses_and_types(image) for image in lookup['image']]
		
		# Create partitions - x IDs per partition
		ids = lookup['id'].unique()

		# Generate random selections per partition 
		counter = 1
		alternator = True
		
		for batch in range(0, n):
			batch_ids = ids
			n_ids = len(ids)
			poses = lookup['pose'].unique()
			## START HERE! subset poses for just the desired ones e.g. 2 action, 2 neutral etc . 
			#if not go pro:
			#  poses = desired poses 
			if 'gopro' not in folder:
				required_images = ['rotation_0', 'rotation_90', 'rotation_270', 'pose_squat', 'pose_fall', 'item_chair', ]
				poses = [i for i in poses if any(b in i for b in required_images)]

			# Default value of n_images is 5
			n_images = n_ids
		
			for i in range(0, len(batch_ids))[::2]:

				if i == 0:
					pose_iterator = i + counter
				if alternator:
					i = i + 1
				if 'gopro' in folder:
					i = i - 1
				if pose_iterator >= len(poses):
					pose_iterator = pose_iterator - len(poses)
				if i >= len(batch_ids):
					continue
				print(f'i: {i}')
				print(f'len batch IDs: {len(batch_ids)}')
				print(f'Pose iterator: {pose_iterator}')
				print(f'batch IDs: {batch_ids}')
				print(f'Batch ids[i] - 1: {batch_ids[i-1]}')
				print(f'Batch ids[i]: {batch_ids[i]}')
				id_images = [x for x in os.listdir(folder_path) if x.startswith(f'{batch_ids[i]}_')]
				print(f'id_images: {id_images}')
				required_image_name = [x for x in id_images if poses[pose_iterator] in x]
				required_image_path = folder_path+'/'+required_image_name[0]
				print(f'Required image name {i} for batch {counter}: {required_image_name}')
				
				source = required_image_path
				destination = batches_output+'/batch_'+f'{counter}'+'/'+required_image_name[0]
				
				#print(id_images)
				shutil.copyfile(source, destination)

				pose_iterator = pose_iterator + 1

				# Write them out to the right files 

				# save to folder
			
			counter = counter + 1
			alternator = (not alternator)

	return None

def create_stool_only_batch(jpg_folder, n, participant_lookups_location, n_images=None):
	n = 1
	for folder in [x for x in os.listdir(jpg_folder) if not x.startswith('.') and not 'batch' in x]:
		if 'gopro' not in folder:
			folder_path = jpg_folder+'/'+folder
			print(f'FOLDER PATH": {folder_path}')
			# search for image: access ID folder, and look for image containing pose name
			batches_output = jpg_folder+f'/turk_chair_batch'
			if not os.path.exists(batches_output):
				os.mkdir(batches_output)
				# Create n folders ready to house batches - one per photogrammetrist
				for i in range(1, n+1):
					os.mkdir(batches_output+'/batch_'+f'{i}')

			if 'gopro' in folder:
				lookup = pd.read_csv(participant_lookups_location+'/gopro_participant_lookup.csv')
			else:
				lookup = pd.read_csv(participant_lookups_location+'/participant_lookup.csv')
			
			# Clean participant table
			lookup = lookup.rename(columns={'Unnamed: 0': 'image'})
			lookup['id'] = [get_participant_id(image) for image in lookup['image']]
			lookup.index = lookup['id']

			# Extract poses
			lookup['pose'] = [extract_poses_and_types(image) for image in lookup['image']]
			
			# Create partitions - x IDs per partition
			ids = lookup['id'].unique()

			# Generate random selections per partition 
			counter = 1
			
			for batch in range(0, n):
				batch_ids = ids
				n_ids = len(ids)
				poses = ['item_chair']
				## START HERE! subset poses for just the desired ones e.g. 2 action, 2 neutral etc . 
				#if not go pro:
				#  poses = desired poses 
				if 'gopro' not in folder:
					required_images = ['item_chair']
					poses = [i for i in poses if any(b in i for b in required_images)]

				# Default value of n_images is 5
				n_images = n_ids
			
				for i in range(0, len(batch_ids)):
					pose_iterator = 0
					print(f'i: {i}')
					print(f'Pose iterator: {pose_iterator}')
					print(f'batch IDs: {batch_ids}')
					id_images = [x for x in os.listdir(folder_path) if x.startswith(f'{batch_ids[i]}_')]
					print(f'id_images: {id_images}')
					required_image_name = [x for x in id_images if poses[pose_iterator] in x]
					required_image_path = folder_path+'/'+required_image_name[0]
					print(f'Required image name {i} for batch {counter}: {required_image_name}')
					
					source = required_image_path
					destination = batches_output+'/batch_'+f'{counter}'+'/'+required_image_name[0]
					
					#print(id_images)
					shutil.copyfile(source, destination)

					pose_iterator = pose_iterator + 1

					# Write them out to the right files 

					# save to folder
				
				counter = counter + 1

	return None


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--jpg_folder', type=str, required=True)
	parser.add_argument('--n_batches', type=int, required=True, help='Number of batches (e.g. same as number of photogrammetrists)')
	parser.add_argument('--participant_lookups_location', type=str, required=True)
	parser.add_argument('--n_photos_per_batch', type=str, required=False)

	args = parser.parse_args()

	jpg_folder = args.jpg_folder # WITHOUT A SLASH AT END
	n = args.n_batches
	participant_lookups_location = args.participant_lookups_location
	n_images = args.n_photos_per_batch

	
	# Obtain the participants true IPD measurement - either add to txt file or rename file 

	create_batches(jpg_folder, n, participant_lookups_location)
	create_stool_only_batch(jpg_folder, n, participant_lookups_location)
	# Mixed batch no longer required.

	return None


if __name__ == "__main__":
	main()

# Tight crop the images
# Create the go pro and studip batches separately
# Create the mixedbatch

#python create_turk_batches.py --jpg_folder /Volumes/OTHER/Input_Photos/7_turk_inputs --n_batches 5  --participant_lookups_location '/Users/sarah/Documents/GitHub/berkeley/forensic-estimation/XX Data'
