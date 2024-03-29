'''
CREATE GENDER LOOKUP TABLE

Script to create lookup table for Smplify-x input

'''
import math
import os
import yaml
import numpy as np
import pandas as pd

import helpers as fn

def ingest_lookup_csv(lookup_path):
    lookup = pd.read_csv(lookup_path)

    return lookup

def create_chair_lookups(df, photos_location, output_location):

    lookup_table = df[['Participant ID', 'gender_identity', 'Height (cm)', 'Weight (kg)', 'IPD']]
    lookup_table['Participant ID'] = fn.generate_ids(58)

    lookup_table.index=lookup_table['Participant ID']
    lookup_table.drop('Participant ID', axis=1, inplace=True)

    photos = os.listdir(photos_location)
    photos = [x for x in photos if not x.startswith('.')]
    photos = [x for x in photos if not x.startswith('ct')]

    photo_lookup = pd.DataFrame(columns = ['gender_identity', 'height_cm', 'weight_kg', 'ipd_cm'], index = photos)

    for photo in photos:
        # Get the ID from the photo
        id_ = ''.join(c for c in photo if c.isdigit())[:3] # Gets first 3 digits regardless of where in the name
        # Marry it to the lookup 
        photo_lookup.loc[photo, 'gender_identity'] = lookup_table.loc[id_, 'gender_identity'].lower()
        photo_lookup.loc[photo, 'height_cm'] = lookup_table.loc[id_, 'Height (cm)']
        photo_lookup.loc[photo, 'weight_kg'] = lookup_table.loc[id_, 'Weight (kg)']
        photo_lookup.loc[photo, 'ipd_cm'] = lookup_table.loc[id_, 'IPD']

    return photo_lookup

def append_lookups(lookup1, lookup2):
    combined = pd.concat([lookup1,lookup2])

    return combined


def get_config_inputs(yaml_file):

    with open(yaml_file, 'r') as file:
        inputs = yaml.load(file, Loader=yaml.FullLoader)

    return inputs



def main():

    yaml_config = '../XX Data/config.yaml'
    inputs = get_config_inputs(yaml_config)

    data_path = inputs['data_path']
    lab_data_path = inputs['lab_data_path']
    cols_to_drop = inputs['cols_to_drop']

    photos_location = inputs['chair_photos_location']
    output_location = '../XX Data'

    df = fn.preprocess(data_path, lab_data_path, cols_to_drop)
    output = create_chair_lookups(df, photos_location, output_location)

    # Write to CSV with new name
    output_file = output_location+'/'+"chair_participant_lookup.csv"
    print(f'OUTPUT FILE: {output_file}')
    output.to_csv(output_file, header=True)


if __name__ == "__main__":
    main()

