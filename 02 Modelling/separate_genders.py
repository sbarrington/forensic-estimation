import shutil
import os
import argparse

import pandas as pd

def create_gender_directories(genders, gender_directory_location):
    for gender in genders:
        gender_root = gender_directory_location+'/'+'3_smplify-x_'+gender
        if not os.path.exists(gender_root):
            os.mkdir(gender_root)
            os.mkdir(gender_root+'/smplify-x_input')
            os.mkdir(gender_root+'/smplify-x_input/images')
            os.mkdir(gender_root+'/smplify-x_input/keypoints')
            os.mkdir(gender_root+'/smplify-x_input/masks')
        #Optional: add in code to transfer the lookup here (presently happens in get_volumes.sh step)
    
    return None

def get_gender(image, lookup_table):
    photo = os.path.basename(image)
    participant_id = get_participant_id(image)
    gender = lookup_table.loc[photo, 'gender_identity'].lower()
    
    return gender 

def get_participant_id(file_or_folder_name):
    return ''.join(c for c in file_or_folder_name if c.isdigit())[:3]

def separate_genders(jobname, lookup_location, gender_directory_location):
    lookup_table = pd.read_csv(lookup_location, index_col=0)
    genders_list = lookup_table['gender_identity'].unique()
    
    create_gender_directories(genders_list, gender_directory_location)
    
    items = ['images', 'keypoints', 'masks']
    
    for item in items:
        photos_location = jobname+'/smplify-x_input/'+item
        images = [x for x in os.listdir(photos_location) if not x.startswith('.')]
        for image in images:
            source_path = photos_location+'/'+image
            image_in = image
            if image[-15:] == '_keypoints.json':
                image_in = image[:-15]+'.png'
            if image[-13:] == '_rendered.png':
                image_in = image[:-13]+'.png'
                
            gender = get_gender(image_in, lookup_table)

            for genders in genders_list:
                if gender == genders:
                    dest_path = gender_directory_location+'/'+'3_smplify-x_'+gender+'/smplify-x_input/'+item+'/'+image
            shutil.copyfile(source_path, dest_path)
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobname', type=str, required=True, help='Location of the photo files that each contain 000.pkl, alongside 000.json and 000.obj from "pose_model_for_simulation.py"')
    parser.add_argument('--lookup_location', type=str, help='Location of participant lookup table')
    parser.add_argument('--gender_directory_location', type=str, default='current', help='Where to store the gender folders (i.e. 3_smplify-x_female folder- usually current dir')

    args = parser.parse_args()
    print(args)

    jobname = args.jobname
    lookup_location = args.lookup_location
    gender_directory_location = str(args.gender_directory_location)

    if gender_directory_location == 'current':
        gender_directory_location = os.getcwd()
    else:
        gender_directory_location = args.gender_directory_location

    separate_genders(jobname, lookup_location, gender_directory_location)

    return None

if __name__ == "__main__":
    main()