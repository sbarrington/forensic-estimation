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

def create_gender_lookup_csv(df, photos_location, output_location):
    
    lookup_table = df[['Participant ID', 'gender_identity']]
    lookup_table['Participant ID'] = fn.generate_ids(58)

    lookup_table.index=lookup_table['Participant ID']
    lookup_table.drop('Participant ID', axis=1, inplace=True)

    photos = os.listdir(photos_location)
    photos = [x for x in photos if not x.startswith('.')]

    photo_lookup = pd.DataFrame(columns = ['gender_identity'], index = photos)

    for photo in photos:
        # Get the ID from the photo
        id_ = photo[:3]
        # Marry it to the lookup 
        photo_lookup.loc[photo, 'gender_identity'] = lookup_table.loc[id_, 'gender_identity'].lower()

    output_file = output_location+'/'+"gender_lookup.csv"
    photo_lookup.to_csv(output_file)

    return f'Lookup table created at {output_file}'

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

    photos_location = inputs['photos_location']
    output_location = inputs['output_location']

    df = fn.preprocess(data_path, lab_data_path, cols_to_drop)
    create_gender_lookup_csv(df, photos_location, output_location)

if __name__ == "__main__":
    main()

