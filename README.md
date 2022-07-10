# Full Pipeline
To view this file as a rendered html doc, do the following:
cmd + shft + p
'Markdown Preview: Preview in browser'
select 'markdown'

simply refresh the browser page when you update the code. 

# 1. Local

#### 1.1. Tidy raw camera files and create participant folders- see data_processing notebook 

#### 1.2. Calibrate 

<b>Calibration & args</b>
````python
yaml_config = '../XX Data/config.yaml'
inputs = get_config_inputs(yaml_config)

photos_location = inputs['photos_location']
n = inputs['n']
output_location_openpose = inputs['output_location_openpose']
output_location_masks = inputs['output_location_masks']
output_location_smplifyx = inputs['output_location_smplifyx']

required_images = inputs['required_images']
````

#### 1.3. Generate padded images and binary masks
````python
ids = dp.generate_ids(n)
#Uncomment for testing only 
#ids = ['003', '014', '050']
````

#### 1.4. When script fails at 35th element for unknown reason:
````python
#ids = ids[35:] # Takes you from ID036 onwards
````
proc.run_all_files_images_folder(photos_location, output_location_openpose, output_location_masks, ids, required_images, method='binary_mask', padding=True, second_output_location=output_location_smplifyx, ext='png')

#### 1.5. Create Gender, height, weight, IPD lookup 
by running the separate script in the 00 directory - store in 3_smplify-x/smplify-x_input folder. 


# 2. Google Drive & CoLab

#### 2.1. Create Gender, height, weight, IPD lookup by running the separate script 
in the 00 directory - store in 3_smplify-x/smplify-x_input folder. 

#### 2.2. Copy the output_location_openpose & output_location_smplifyx 
into google drive folders with same names ###

#### 2.3. RUN OPENPOSE (colab notebook)

#### 2.4. GDRIVE - download openpose results from 3_smplify-x/smplify-x_input/keypoints folder 
Unzip this 'keypoints' file in the 3_smplify-x/smplify-x_input local directory

# 3. Deep-learning VM

#### 3.1. GDRIVE/LOCAL - STEP 5: zip & transfer whole local 3_smplify-x to VM via SSH 
#### 3.2. SEPARATE GENDERS go from 3_smplify-x -> 3_smplify-x_female & male
On VM, run: bash separate_genders.py --jobname 3_smplify-x --lookup_location 3_smplify-x/smplify-x_input/participant_lookup.csv --gender_directory_location current

#### 3.3. RUN 2X JOBS, ONE PER GENDER
#### 3.4. RUN 2X 'GET VOLUMES', ONE PER GENDER (I NEED TO FINISH THE VOLUME EXTRACTION TO CSV)
	

#### 3.5. VM - STEP X: RUN SMPLIFY-X CODE for first gender, repeat for second gender
```bash
conda activate hw_render
bash fit_images_sil.sh ~/3_smplify-x_male male results 3000 0.01 
bash fit_images_sil.sh ~/3_smplify-x_female female results 3000 0.01 
```

#### 3.6. VM - STEP X: RUN VOLUME SIMULATION 
```bash
bash get_volumes.sh ~/3_smplify-x_female female 3_smplify-x/smplify-x_input/participant_lookup.csv
bash get_volumes.sh ~/3_smplify-x_male male 3_smplify-x/smplify-x_input/participant_lookup.csv
```

#### 3.7. TRANSFER RESULTS TO LOCAL ### [SSH + ZIP FILE?]
Zip results for browsing locally: 
```bash
zip -r results_female.zip 3_smplify-x_female/results/
zip -r results_male.zip 3_smplify-x_male/results/
```
