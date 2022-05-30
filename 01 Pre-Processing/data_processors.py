import numpy as np
import pandas as pd

'''
May 2022
Sarah Barrington

Data processing functions for creation and structuring of images from Forensic Estimation Project.

INPUT: JPEG files organised within participant ID folders
OUTPUT: structured and re-named JPEG files allowing reference by participant and photo type

'''

def generate_ids(n):
    '''
    n = total number of study participants
    '''
    IDs = [str(x) for x in list(range(1,n+1))]
    for i in range(len(IDs)):
        IDs[i] = '0'+IDs[i]
        if i < 9:
            IDs[i] = '0'+IDs[i]

    print(f'Total number of IDs generated: {len(IDs)}')

    return IDs

def create_folders(IDs):
    for folder_name in IDs:
        if data_location+'/'+folder_name:
            print("already exists")
        else:
            print("Files do not already exist.")
            print(f"Creating {len(IDs)} new files. These may overwrite existing files.")
            q = input('CONTINUE? Y/n')
            if q=='Y':
                print('Making new directories...')
                os.mkdir(data_location+'/'+folder_name)
    return None


def check_n_photos(data_location, less_than=False, more_than=False):
    files = os.listdir(data_location)
    ids = [x for x in files if not x.startswith('.')]

    for id_ in ids:
        photos = os.listdir(data_location+'/'+id_)
        photos = [x for x in photos if not x.startswith('.')]

        # If more than 24 photos, print out
        n_photos = len(photos)
        if less_than:
            if  n_photos < 24:
                print(f'ID {id_} has {n_photos} photos.')
        elif more_than:
            if  n_photos > 24:
                print(f'ID {id_} has {n_photos} photos.')
        elif  n_photos != 24:
            print(f'ID {id_} has {n_photos} photos.')
            
    return None

def rename_files(ids, renames, retain_original_name=False):
    for id_ in ids:
        photos = os.listdir(data_location+'/'+id_)
        photos = [x for x in photos if not x.startswith('.')]
        photos = sorted(photos)

        for i in range(len(photos)):
            source = data_location+'/'+id_+'/'+photos[i]
            if retain_original_name:
                dest = data_location+'/'+id_+'/'+id_+'_'+renames[i]+'_'+photos[i]
            else:
                dest = data_location+'/'+id_+'/'+id_+'_'+renames[i]+'.jpg'
            os.rename(source, dest)
        
        print(f'Completed renaming files for ID {id_}')
    
    return None

