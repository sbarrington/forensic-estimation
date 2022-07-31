# Full Pipeline
To view this file as a rendered html doc, do the following:
cmd + shft + p
'Markdown Preview: Preview in browser'
select 'markdown'

simply refresh the browser page when you update the code. 

# 1. Local

#### 1.1. Tidy raw camera files and create participant folders- see data_processing notebook 
Output is the 'Input_Images/1_original_jpgs' folder. This has already been done and presently exists on the shared research Google Drive folder, and so can be downloaded directly without the need to re-run the original structuring and renaming script. 

#### 1.1. Run full_pipeline.py script locally

<b>Calibration & args</b>
Check the config.yaml file has the correct config set up. 
Ensure config.yaml file can be read into the full_pipeline.py scrip as follows:
````python
yaml_config = '../XX Data/config.yaml'
inputs = get_config_inputs(yaml_config)
````
<b>Folders</b>
Ensure the various output folders exist: these are listed in the config.yaml file, e.g. 'Input_Photos/2_openpose_input'

<b>Running the script</b>
Navigate to 01 Preprocessing folder containing full_pipeline.py script
Run:
```bash
python full_pipeline.py
```

<b> Notes: generating the padded images and binary masks</b>b>
The full_pipeline script generates all 58 IDs (this can be changed in the config.yaml file if required). The pipeline script can be calibrated via the config file through uncommenting one of the pre-selected set ups (e.g. testing only, gopro, or studio images).

Optional: if script fails at 35th element for unknown reason:
* re-run script with the following uncommmented
````python
#ids = ids[35:] # Takes you from ID036 onwards
````
##### 1.1.1. using photoshop to create binbnary masks instead
* In this case, the binary mask creation will be done 
Uncomment the photoshop options in the config gile to create the input files, included padded. 
* Run the 'create padded masks.py' script, using the same config set up:
```bash
python create_padded_masks.py
```
##### 1.1.2. Batch processing in photoshop
* Then, run the batch processing in photoshop:
> * Open photoshop
> * File > automate > batch > create_binary_mask
> * Select the appropriate input and output folders (NOTE: These are both unpadded so make sure this is a temporary location, NOT the smplfy-x input)
> * Run

For reference, the batch processing steps (actions > new action > record):

1. Select floor
2. Delete it & select white infill
3. Select object (person)
4. Edit > Fill > white 
5. Right click > select inverse
6. Edit > fill > black
7. Quick export as PNG

<b> Note: for GoPro batch processing: </b>
* Because the GoPro images all have the subject in different locations, 5 different folders must be created and run separately for each pose
* E.g. gopro_walk, gopro_steps, gopro_topstep etc.
* Each one must have the participant selected with the magic wand tool manually.

##### 1.1.3. Manually clean up any failed masks

Eyeball results from photoshop batch processing and manually re-import and select these images into photoshop. 

##### 1.1.4.Pad, clean and resize the photoshop outputs
Run twice- once for studio and once for GoPro
```bash
python pad_photoshop_masks.py --inputsforstudio
python pad_photoshop_masks.py --inputsforgopro

```

#### 1.2. Create Gender, height, weight, IPD lookup 
by running the separate script in the 00 directory - store in XX_smplify-x/smplify-x_input folder. 


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

<b> Note: failure cases: </b>
* Sometimes failures occur when the model fit didn't work, so the image directory exists in 'results', but doesnt contain any information. 
* Presently, the code does not skip these cases, but exits with an error 
* Manually, remove these directories (rm -R path_to_directory/) and then re run the script

<b> Failure cases must be recorded alongside failure rate (e.g. 3/850 images failed)</b>

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

## Reference Commands

To run an SSH job that continues after the SSH window closes/internet connection drops:
- Add the nohup command infront of the usual bash script 
- Can direct it to either an output.txt file or it'll go to a nohup.out file by default 
- e.g. nohup usual_bash_command > output.txt

python separate_genders.py --jobname 3_smplify-x_maskcorrection --lookup_location 3_smplify-x_maskcorrection/smplify-x_input/participant_lookup.csv --gender_directory_location 'current'

python separate_genders.py --jobname 5_smplify-x_gopro --lookup_location 5_smplify-x_gopro/smplify-x_input/participant_lookup.csv --gender_directory_location 'current'

WINDOW 1
conda activate hw_render
bash fit_images_sil.sh ~/3_smplify-x_maskcorrection_male male results 3000 0.01 
WINDOW 2
# In second SSH connection window:
conda activate hw_render
bash fit_images_sil.sh ~/3_smplify-x_maskcorrection_female female results 3000 0.01 


WINDOW 1
conda activate hw_render
bash fit_images_sil.sh ~/5_smplify-x_gopro_male male results 3000 0.01 
WINDOW 2
# In second SSH connection window:
conda activate hw_render
bash fit_images_sil.sh ~/5_smplify-x_gopro_female female results 3000 0.01 

Commands:
```bash
# Mask correction only
bash get_volumes_and_heights.sh ~/3_smplify-x_maskcorrection_female female 3_smplify-x_maskcorrection/smplify-x_input/participant_lookup.csv maskcorrection_overall_results_female.csv

bash get_volumes_and_heights.sh ~/3_smplify-x_maskcorrection_male male 3_smplify-x_maskcorrection/smplify-x_input/participant_lookup.csv maskcorrection_overall_results_male.csv

# GoPro - legacy, before IPD lookup and adjustment
bash get_volumes_and_heights.sh ~/5_smplify-x_gopro_male male 5_smplify-x_gopro/smplify-x_input/participant_lookup.csv gopro_hw_overall_results_male.csv
```

## Updated Process: With Neutral-Pose IPD Adjustment
Additional steps:
* Create an IPD adjustment lookup table with each participant's adjusted IPD
* Run the Studio and GoPro images using two different scripts = 'gopro_get_volumes_and_heights.sh' and 'get_volumes_and_heights.sh'
* Note that the 'get_volumes_and_heights_from_mesh.py' script has been updated to <b>only</b> use adjusted IPD. To revert back to using the measured IPD, this script will need to be updated
* NOTE: GO PRO SCRIPT ALSO TAKES AN ADDITONAL ARGUMENT FOR THE IPD ADJUSTMENT TABLE (that lives in the studio folder as this is where the neutral poses are, and where the lookups were calculated)

<b>NOTE: in order to run the height and weight extractions only (e.g. not the re-posing to obtain the 'posed' models), comment out the for-loop section in 'get_volumes_and_heights.sh' that runs 'smplify-x-sil/smplifyx/pose_model_for_simulation.py'</b>

```bash
# FIRST: CREATE ADJUSTED IPD LOOKUP
python create_adjusted_ipd_lookup.py --jobname ~/3_smplify-x_maskcorrection_female
python create_adjusted_ipd_lookup.py --jobname ~/3_smplify-x_maskcorrection_male

# THEN: IPD correction, either studio or GoPro
bash get_volumes_and_heights.sh ~/3_smplify-x_maskcorrection_male male 3_smplify-x_maskcorrection/smplify-x_input/participant_lookup.csv ipdcorr_overall_results_male.csv

bash get_volumes_and_heights.sh ~/3_smplify-x_maskcorrection_female female 3_smplify-x_maskcorrection/smplify-x_input/participant_lookup.csv ipdcorr_overall_results_female.csv

# GoPro with IPD adjustment
bash gopro_get_volumes_and_heights.sh ~/5_smplify-x_gopro_male male 5_smplify-x_gopro/smplify-x_input/participant_lookup.csv gopro_ipdcorr_overall_results_male.csv 3_smplify-x_maskcorrection_male/smplify-x_input/adjusted_ipd_lookup.csv

bash gopro_get_volumes_and_heights.sh ~/5_smplify-x_gopro_female female 5_smplify-x_gopro/smplify-x_input/participant_lookup.csv gopro_ipdcorr_overall_results_female.csv 3_smplify-x_maskcorrection_female/smplify-x_input/adjusted_ipd_lookup.csv
```


