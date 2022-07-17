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
Get IDs:
````python
ids = dp.generate_ids(n)
#Uncomment for testing only 
#ids = ['003', '014', '050']
````

Run through processing for all files:
```python
proc.run_all_files_images_folder(photos_location, output_location_openpose, output_location_masks, ids, required_images, method='binary_mask', padding=True, second_output_location=output_location_smplifyx, ext='png')
```

Optional: if script fails at 35th element for unknown reason:
* re-run script with the following uncommmented
````python
#ids = ids[35:] # Takes you from ID036 onwards
````

#### 1.4. Create Gender, height, weight, IPD lookup 
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

#### 3.1. Transfer inputs Job Folder to VM
Locally: Zip & transfer whole local 3_smplify-x to VM via SSH 
VM: Unzip the file 

#### 3.2. Separate inputs by gender
Go from 3_smplify-x -> 3_smplify-x_female & male

For test case:
```bash
#python separate_genders.py --jobname smplify-x_test --lookup_location 3_smplify-x/smplify-x_input/participant_lookup.csv --gender_directory_location TEST
```
For real case:
```bash
python separate_genders.py --jobname 3_smplify-x --lookup_location 3_smplify-x/smplify-x_input/participant_lookup.csv --gender_directory_location 'current'
```

#### 3.3. Run multiple jobs, one per gender 
RUN SMPLIFY-X CODE for first gender, repeat for other genders.

<b> Note: use 2 separate SSH connection windows and run one job in each!</b>

Example:
```bash
conda activate hw_render
bash fit_images_sil.sh ~/3_smplify-x_male male results 3000 0.01 

# In second SSH connection window:
conda activate hw_render
bash fit_images_sil.sh ~/3_smplify-x_female female results 3000 0.01 
```
### 3.4. Run Volume and Height simulation, one per gender
> [!] <b>Known error:  
> padded_037_rotation_135_DSC_0642 results folder not populated from previous step.  
> manually remove padded_037_rotation_135_DSC_0642, then re-fit step 3.3. to single folder at later stage. </b> 
For the height and volume combined script:
```bash

bash get_volumes_and_heights.sh ~/3_smplify-x_female female 3_smplify-x/smplify-x_input/participant_lookup.csv hw_overall_results.csv

bash get_volumes_and_heights.sh ~/3_smplify-x_male male 3_smplify-x/smplify-x_input/participant_lookup.csv hw_overall_results_male.csv

```

#### Legacy - 3.4. Run volume simulation, one per gender

Example:
```bash
#bash get_volumes.sh ~/3_smplify-x_female female 3_smplify-x/smplify-x_input/participant_lookup.csv
#bash get_volumes.sh ~/3_smplify-x_male male 3_smplify-x/smplify-x_input/participant_lookup.csv
```

#### 3.5. Transfer results to local for analysis
For CSV output:
* Manually SSH transfer results CSVs (one per gender) to local

For full results from VM: 
* Zip results for browsing locally

Example:
```bash
zip -r results_female.zip 3_smplify-x_female/results/
zip -r results_male.zip 3_smplify-x_male/results/
```
* Transfer via SSH

Locally:
* Unzip
* Explore using Python

# 4. Local Analysis of Volumes

#### 4.1 Open and merge gender volume CSVs (e.g. male, female) in Python 

#### 4.2 Produce volume vs. true weight plot 


Use height method from reposed script 
'height from mesh.py'
Use the re-posed OBJ file so that its in neutral pose. Run on batch. 



Treat separate distributions/regression model inputs 

Another baseline:
- use ground truth height to scale model - this is how good you can do with the 3d modelling with a beter height. 
- Also do the 3d height estimation + weight regression
