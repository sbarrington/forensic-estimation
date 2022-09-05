import pickle
import math
import os
import argparse
import random

import pandas as pd
import numpy as np

from PIL import Image

def get_participant_id(file_or_folder_name):
		return ''.join(c for c in file_or_folder_name if c.isdigit())[:3]

def extract_poses_and_types(image):
    return image[11:-13]

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--jpg_folder', type=str, required=True)
	parser.add_argument('--n_batches', type=int, required=True, help='Number of batches (e.g. same as number of photogrammetrists)')
	parser.add_argument('--participant_lookup_csv', type=str, required=True)
	parser.add_argument('--n_photos_per_batch', type=str, required=False)

	args = parser.parse_args()

	jpg_folder = args.jpg_folder # WITHOUT A SLASH AT END
	n = args.n_batches
	participant_lookup_location = args.participant_lookup_csv
	n_images = args.n_photos_per_batch

	batches_output = jpg_folder+'/photogrammetrist_batches'
	if not os.path.exists(batches_output):
		os.mkdir(batches_output)
		# Create n folders ready to house batches - one per photogrammetrist
		for i in range(1, n+1):
			os.mkdir(batches_output+'/batch_'+f'{i}')

	lookup = pd.read_csv(participant_lookup_location)
	
	# Clean participant table
	lookup = lookup.rename(columns={'Unnamed: 0': 'image'})
	lookup['id'] = [get_participant_id(image) for image in lookup['image']]
	lookup.index = lookup['id']

	# Extract poses
	lookup['pose'] = [extract_poses_and_types(image) for image in lookup['image']]
	
	# Create partitions - x IDs per partition
	ids = lookup['id'].unique()
	random.seed(4)
	random.shuffle(ids)
	id_batches = np.array_split(ids, n)
	print(id_batches)
	partitions = []
	for i in range(0, n):
		partition = lookup[lookup['id'].isin(id_batches[i])]
		partitions.append(partition)

	# Generate random selections per partition 
	counter = 1
	for partition in partitions:
		batch_ids = []
		batch_poses = []
		ids = partition['id'].unique()
		n_ids = len(ids)
		poses = partition['pose'].unique()

		# Default value of n_images is 5
		if n_images is None: 
			n_images = 5
		
		# for ID in partition[ids], select pose (i)
		for i in range(0, len(ids)):
			if i >= n_images:
				continue
			id_ = ids[i]
			if i < len(poses):
				pose = poses[i]
			else:
				pose = poses[i-len(poses)]
			batch_ids.append(id_)
			batch_poses.append(pose)

		print(f'batch {counter}:')
		print(batch_ids)
		print(batch_poses)
			
		# search for image: access ID folder, and look for image containing pose name
		for i in range(0, len(batch_ids)):
			id_folder = jpg_folder+'/'+batch_ids[i]
			id_images = [x for x in os.listdir(id_folder) if not x.startswith('.')]
			required_image_name = [x for x in id_images if batch_poses[i] in x]
			required_image_path = id_folder+'/'+required_image_name[0]
			
			# Strip metadata
			image = Image.open(required_image_path)

			# next 3 lines strip exif
			data = list(image.getdata())
			image_without_exif = Image.new(image.mode, image.size)
			image_without_exif.putdata(data)
			image_without_exif = image_without_exif.rotate(180)

			image_without_exif.save(batches_output+'/batch_'+f'{counter}'+'/'+required_image_name[0])
			# Write them out to the right files 

			# save to folder
		counter = counter + 1

	# Obtain the participants true IPD measurement - either add to txt file or rename file 


	

	#print(partitions)


	#partitions = np.array_split(lookup, n)
	#print(partitions)

	return None


if __name__ == "__main__":
	main()

#python create_photogrammetrist_batches.py --jpg_folder /Volumes/OTHER/Input_Photos/1_original_jpgs --n_batches 10  --participant_lookup_csv '/Users/sarah/Documents/GitHub/berkeley/forensic-estimation/XX Data/gopro_participant_lookup.csv'
