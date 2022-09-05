import http.client
import json
import os
import io
import time
import yaml
import requests
import zipfile

import matplotlib.pyplot as plt
import plotly.express as px

import pandas as pd
import numpy as np

from datetime import date
from scipy.stats import norm
from scipy import stats
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_absolute_percentage_error
import statsmodels.api as sm
from scipy.stats import sem

def create_dict_of_dicts(experiments):
    dictofdicts = {}
    for experiment in experiments:
        dictofdicts[experiment] = {}
        for gender in ['male', 'female', 'overall']:
            dictofdicts[experiment][gender] = {}
            for item in ['mae', 'mape']:
                dictofdicts[experiment][gender][item] = np.nan
        
    return dictofdicts

def create_summary_table(experiments, resultsdict, units='kg'):
    rows = experiments
    
    if units == 'kg':

        columns = [['Male','Male', 
                    'Female','Female',
                    'Overall', 'Overall'],
                ['MAPE (%)','MAE (kg)',
                 'MAPE (%)','MAE (kg)',
                 'MAPE (%)','MAE (kg)',#, 
                    #'Standard Error','Standard Error','Standard Error', 
                    #'R^2 Value','R^2 Value','R^2 Value'
                   ]]
    elif units == 'cm': 
        columns = [['Male','Male', 
                    'Female','Female',
                    'Overall', 'Overall'],
                ['MAPE (%)','MAE (cm)',
                 'MAPE (%)','MAE (cm)',
                 'MAPE (%)','MAE (cm)',#, 
                    #'Standard Error','Standard Error','Standard Error', 
                    #'R^2 Value','R^2 Value','R^2 Value'
                   ]]
    elif units == 'kg/cm': 
        columns = [['Male','Male', 
                    'Female','Female',
                    'Overall', 'Overall'],
                ['MAPE (%)','MAE (kg/cm)',
                 'MAPE (%)','MAE (kg/cm)',
                 'MAPE (%)','MAE (kg/cm)',#, 
                    #'Standard Error','Standard Error','Standard Error', 
                    #'R^2 Value','R^2 Value','R^2 Value'
                   ]]
    tuples = list(zip(*columns))
    multicol = pd.MultiIndex.from_tuples(tuples)

    results_gendered = pd.DataFrame(columns=multicol, index=rows)

    results_gendered

    for row in results_gendered.index:
        if units == 'kg':
            results_gendered.loc[row, ('Male', 'MAE (kg)')] = resultsdict[row]['male']['mae']
            results_gendered.loc[row, ('Female', 'MAE (kg)')] = resultsdict[row]['female']['mae']
            results_gendered.loc[row, ('Overall', 'MAE (kg)')] = resultsdict[row]['overall']['mae']
        
        elif units == 'cm':
            results_gendered.loc[row, ('Male', 'MAE (cm)')] = resultsdict[row]['male']['mae']
            results_gendered.loc[row, ('Female', 'MAE (cm)')] = resultsdict[row]['female']['mae']
            results_gendered.loc[row, ('Overall', 'MAE (cm)')] = resultsdict[row]['overall']['mae']

        results_gendered.loc[row, ('Male', 'MAPE (%)')] = resultsdict[row]['male']['mape']
        results_gendered.loc[row, ('Female', 'MAPE (%)')] = resultsdict[row]['female']['mape']
        results_gendered.loc[row, ('Overall', 'MAPE (%)')] = resultsdict[row]['overall']['mape']
    
    
    results_gendered.loc[:,('Male', 'MAPE (%)')] = results_gendered.loc[:,('Male', 'MAPE (%)')].astype(float)
    results_gendered = results_gendered.sort_values(by=[('Male', 'MAPE (%)')], ascending=True)

    results_gendered.loc[:,('Male', 'MAPE (%)')] = results_gendered.loc[:,('Male', 'MAPE (%)')].astype(str)+'%'
    results_gendered.loc[:,('Female', 'MAPE (%)')] = results_gendered.loc[:,('Female', 'MAPE (%)')].astype(str)+'%'
    results_gendered.loc[:,('Overall', 'MAPE (%)')] = results_gendered.loc[:,('Overall', 'MAPE (%)')].astype(str)+'%'
    
    results_gendered = results_gendered.replace('nan%', 'NaN')
    results_gendered = results_gendered.replace('NaN%', 'NaN')
    results_gendered = results_gendered.replace('NaN', '')
    results_gendered = results_gendered.fillna('')
    
    return results_gendered

def generate_final_results_table(weight_results, height_results):
    
    final_results_weight = weight_results
    final_results_height = height_results
    
    columns = [list(x) for x in final_results_weight.columns]
    for i in range(0, len(columns)):
        columns[i][1] = columns[i][1].replace('(kg)', '(cm/kg)')

    final_results_weight.columns = [tuple(x) for x in columns]
    final_results_weight.columns = pd.MultiIndex.from_tuples(final_results_weight.columns)

    columns = [list(x) for x in final_results_height.columns]
    for i in range(0, len(columns)):
        columns[i][1] = columns[i][1].replace('(cm)', '(cm/kg)')

    final_results_height.columns = [tuple(x) for x in columns]
    final_results_height.columns = pd.MultiIndex.from_tuples(final_results_height.columns)

    final_results = pd.concat({'Height': final_results_height, 'Weight': final_results_weight}, names=[''])

    return final_results

def calculate_mae(y_pred, y_true, printout=True):
    
    y_pred = y_pred[y_pred.notnull()]
    y_true = y_true[y_pred.notnull()]
    #mean_absolute_error(results['median_est_weight_kg'][results['median_est_weight_kg'].notnull()], results['act_weight_kg'][results['median_est_weight_kg'].notnull()])
    
    regression_mae = round(mean_absolute_error(y_true, y_pred), 3)
    regression_mae_perc = round(100*mean_absolute_percentage_error(y_true, y_pred), 2)

    if printout:
        print(f'MAE = {regression_mae} units')
        print(f'{regression_mae_perc}%')

    return regression_mae, regression_mae_perc


def get_linear_coefs(X, Y):
    X = sm.add_constant(X)
    model = sm.OLS(Y,X)
    regression_results = model.fit()
    intercept = regression_results.params[0]
    v1 = regression_results.params[1]
    print(intercept)
    print(v1)
    
    return intercept, v1

def start_and_obtain_qualtrics_export(survey_url, qualtrics_api_token, out_path, time_stamp):
    print('Initiaiting qualtrics export')

 
    conn = http.client.HTTPSConnection("ca1.qualtrics.com")
    url = survey_url

    headers = {
        'Content-Type': "application/json",
        'X-API-TOKEN': qualtrics_api_token
        }
    data = {
        "format": "csv"
        }

    downloadRequestResponse = requests.request("POST", url, json=data, headers=headers)
    print(downloadRequestResponse.json())

    progressId = downloadRequestResponse.json()['result']['progressId']
    progress_url = url + progressId 

    progressRequestResponse = requests.request("GET", progress_url, json=data, headers=headers)


    while progressRequestResponse.json()['result']['status'] == 'inProgress':
        print('Export not ready, sleeping for 5s')
        time.sleep(5)
        print(progressRequestResponse.json()['result'])


    requestId = progressRequestResponse.json()['result']['fileId']
    request_url = url + requestId + '/file'
    print(request_url)
    fileRequestResponse = requests.request("GET", request_url, headers=headers, stream=True)
    print(fileRequestResponse)

    zipfile.ZipFile(io.BytesIO(fileRequestResponse.content)).extractall('qualtrics_results')
    os.rename("qualtrics_results/Height_Weight_Estimation_Draft3.csv", out_path+f'/Height_Weight_Estimation_Draft3_{time_stamp}.csv')
    print('Results unzipped')

    print('Reading in qualtrics file')

    files = [out_path+'/'+file for file in os.listdir(out_path) if not file.startswith('.') and '.csv' in file]
    latest_file = max(files, key=os.path.getctime)

    df = pd.read_csv(f"{latest_file}")

    return df

def get_config_inputs(yaml_file):

    with open(yaml_file, 'r') as file:
        inputs = yaml.load(file, Loader=yaml.FullLoader)

    return inputs

def extract_questions(df, qsf_file):

    with open(qsf_file) as json_file:
        data = json.load(json_file) 
        
    images = []
    qids = []
    export_tags = []

    for i in range(0, len(data['SurveyElements'])):
        try:
            text = data['SurveyElements'][i]['Payload']['QuestionText']
        except: 
            continue
        if 'https://' in text:
            images.append(text.split('"')[3].split('/')[-1])
            qids.append(data['SurveyElements'][i]['Payload']['QuestionID'])
            export_tags.append(data['SurveyElements'][i]['Payload']['DataExportTag'])

    images = [image.replace('%20', ' ') for image in images]

    return images, qids, export_tags

def generate_overall_table(df, lookup):
    ids = []
    qs = []
    est_heights = []
    est_weights = []
    act_heights = []
    act_weights = []
    genders = []

    df = df.drop([0, 1], axis=0)

    for column in df.columns:
        if 'Q' in column:
            qid = column.split('_')[0]
            try:
                id_ = lookup.loc[lookup['export_tag_qualtrics'] == qid, 'participant_id'].values[0]
                gender = lookup.loc[lookup['export_tag_qualtrics'] == qid, 'gender_identity'].values[0]
                image = lookup.loc[lookup['export_tag_qualtrics'] == qid, 'image'].values[0]
                image_root = image.split('.')[0].replace('padded_', '')
                
                if '_1' in column:
                    
                    av_height_ft = np.nanmedian([float(item)*30.48 for item in pd.to_numeric(df[column])]) # Convert to CM
                    est_heights.append(av_height_ft)

                    act_height = lookup.loc[lookup['export_tag_qualtrics'] == qid, 'height_cm'].values[0]
                    act_weight = lookup.loc[lookup['export_tag_qualtrics'] == qid, 'weight_kg'].values[0]
                    act_heights.append(act_height)
                    act_weights.append(act_weight)
                    genders.append(gender)

                    if 'gopro' in image_root:
                        batch = 'gopro'
                    elif 'chair' in image_root:
                        batch = 'chair'
                    else:
                        batch = 'studio'
                    ids.append(id_+'_'+batch)
                    qs.append(qid)

                if '_2' in column:
                    av_height_in = np.nanmedian([float(item)*2.54 for item in pd.to_numeric(df[column])])
                    est_heights[-1] = est_heights[-1] + av_height_in
                if '_3' in column:
                    av_weight = np.nanmedian([float(item)*0.453592 for item in pd.to_numeric(df[column])])
                    est_weights.append(av_weight)
            except:
                continue

    results = pd.DataFrame({'id':ids, 'q_export_tag':qs, 'gender': genders, 'median_est_height_cm':est_heights, 'median_est_weight_kg':est_weights,
                       'act_height_cm':act_heights, 'act_weight_kg':act_weights})
    results['error_height'] = results['median_est_height_cm'] - results['act_height_cm']
    results['error_weight'] = results['median_est_weight_kg'] - results['act_weight_kg']


    return results

def merge_questions_and_lookup(df, images, qids, export_tags, lookup_location):
    lookup = pd.read_csv(lookup_location+'/participant_lookup.csv')
    gopro_lookup = pd.read_csv(lookup_location+'/gopro_participant_lookup.csv')
    chair_lookup = pd.read_csv(lookup_location+'/chair_participant_lookup.csv')
    lookup = lookup.append(gopro_lookup)
    lookup = lookup.append(chair_lookup)
    lookup['participant_id'] = ''
    lookup['qid_qualtrics'] = ''
    lookup['export_tag_qualtrics'] = ''
    lookup = lookup.rename(columns={'Unnamed: 0':'image'})

    for i in range(0, len(images)):
        image_root = images[i].split(' ')[0]
        image_root = images[i].split('.')[0]
        lookup.loc[lookup['image'].str.contains(image_root), 'qid_qualtrics'] = qids[i]
        lookup.loc[lookup['image'].str.contains(image_root), 'export_tag_qualtrics'] = export_tags[i]
        lookup.loc[lookup['image'].str.contains(image_root), 'participant_id'] = images[i].split('_')[0]

    results = generate_overall_table(df, lookup)
    print('results.head from merge questions an dlookup function:')
    print(results.head())

    

    return(results)

def generate_accuracies(results):
    turk_experiments = ['Turk: studio', 'Turk: "wild"', 'Turk: reference object']
    turk_weight_resultsdict = create_dict_of_dicts(turk_experiments)
    turk_height_resultsdict = create_dict_of_dicts(turk_experiments)

    df = results[results['id'].str.contains('gopro')]

    # GOPRO WEIGHT
    # Split by gender
    female = df[df['gender']=='female']
    male = df[df['gender']=='male']

    # Overall
    mae_weight, mape_weight = calculate_mae(y_pred=df['median_est_weight_kg'], y_true=df['act_weight_kg'])

    turk_weight_resultsdict['Turk: "wild"']['overall']['mae'] = mae_weight
    turk_weight_resultsdict['Turk: "wild"']['overall']['mape'] = mape_weight

    # Male
    mae_weight, mape_weight = calculate_mae(y_pred=male['median_est_weight_kg'], y_true=male['act_weight_kg'])

    turk_weight_resultsdict['Turk: "wild"']['male']['mae'] = mae_weight
    turk_weight_resultsdict['Turk: "wild"']['male']['mape'] = mape_weight

    # Female
    mae_weight, mape_weight = calculate_mae(y_pred=female['median_est_weight_kg'], y_true=female['act_weight_kg'])

    turk_weight_resultsdict['Turk: "wild"']['female']['mae'] = mae_weight
    turk_weight_resultsdict['Turk: "wild"']['female']['mape'] = mape_weight
    

    # GOPRO HEIGHT
    df = results[results['id'].str.contains('gopro')]

    # Split by gender
    female = df[df['gender']=='female']
    male = df[df['gender']=='male']

    # Overall
    mae_height, mape_height = calculate_mae(y_pred=df['median_est_height_cm'], y_true=df['act_height_cm'])

    turk_height_resultsdict['Turk: "wild"']['overall']['mae'] = mae_height
    turk_height_resultsdict['Turk: "wild"']['overall']['mape'] = mape_height

    # Male
    mae_height, mape_height = calculate_mae(y_pred=male['median_est_height_cm'], y_true=male['act_height_cm'])

    turk_height_resultsdict['Turk: "wild"']['male']['mae'] = mae_height
    turk_height_resultsdict['Turk: "wild"']['male']['mape'] = mape_height

    # Female
    mae_height, mape_height = calculate_mae(y_pred=female['median_est_height_cm'], y_true=female['act_height_cm'])

    turk_height_resultsdict['Turk: "wild"']['female']['mae'] = mae_height
    turk_height_resultsdict['Turk: "wild"']['female']['mape'] = mape_height

    # TURK CHAIR WEIGHT
    df = results[results['id'].str.contains('chair')]

    # Split by gender
    female = df[df['gender']=='female']
    male = df[df['gender']=='male']

    # Overall
    mae_weight, mape_weight = calculate_mae(y_pred=df['median_est_weight_kg'], y_true=df['act_weight_kg'])

    turk_weight_resultsdict['Turk: reference object']['overall']['mae'] = mae_weight
    turk_weight_resultsdict['Turk: reference object']['overall']['mape'] = mape_weight

    # Male
    mae_weight, mape_weight = calculate_mae(y_pred=male['median_est_weight_kg'], y_true=male['act_weight_kg'])

    turk_weight_resultsdict['Turk: reference object']['male']['mae'] = mae_weight
    turk_weight_resultsdict['Turk: reference object']['male']['mape'] = mape_weight

    # Female
    mae_weight, mape_weight = calculate_mae(y_pred=female['median_est_weight_kg'], y_true=female['act_weight_kg'])

    turk_weight_resultsdict['Turk: reference object']['female']['mae'] = mae_weight
    turk_weight_resultsdict['Turk: reference object']['female']['mape'] = mape_weight

    # TURK CHAIR HEIGHT
    df = results[results['id'].str.contains('chair')]

    # Split by gender
    female = df[df['gender']=='female']
    male = df[df['gender']=='male']

    # Overall
    mae_height, mape_height = calculate_mae(y_pred=df['median_est_height_cm'], y_true=df['act_height_cm'])

    turk_height_resultsdict['Turk: reference object']['overall']['mae'] = mae_height
    turk_height_resultsdict['Turk: reference object']['overall']['mape'] = mape_height

    # Male
    mae_height, mape_height = calculate_mae(y_pred=male['median_est_height_cm'], y_true=male['act_height_cm'])

    turk_height_resultsdict['Turk: reference object']['male']['mae'] = mae_height
    turk_height_resultsdict['Turk: reference object']['male']['mape'] = mape_height

    # Female
    mae_height, mape_height = calculate_mae(y_pred=female['median_est_height_cm'], y_true=female['act_height_cm'])

    turk_height_resultsdict['Turk: reference object']['female']['mae'] = mae_height
    turk_height_resultsdict['Turk: reference object']['female']['mape'] = mape_height

    # TURK STUDIO WEIGHT
    df = results[results['id'].str.contains('studio')]

    # Split by gender
    female = df[df['gender']=='female']
    male = df[df['gender']=='male']

    # Overall
    mae_weight, mape_weight = calculate_mae(y_pred=df['median_est_weight_kg'], y_true=df['act_weight_kg'])

    turk_weight_resultsdict['Turk: studio']['overall']['mae'] = mae_weight
    turk_weight_resultsdict['Turk: studio']['overall']['mape'] = mape_weight

    # Male
    mae_weight, mape_weight = calculate_mae(y_pred=male['median_est_weight_kg'], y_true=male['act_weight_kg'])

    turk_weight_resultsdict['Turk: studio']['male']['mae'] = mae_weight
    turk_weight_resultsdict['Turk: studio']['male']['mape'] = mape_weight

    # Female
    mae_weight, mape_weight = calculate_mae(y_pred=female['median_est_weight_kg'], y_true=female['act_weight_kg'])

    turk_weight_resultsdict['Turk: studio']['female']['mae'] = mae_weight
    turk_weight_resultsdict['Turk: studio']['female']['mape'] = mape_weight

    # TURK STUDIO HEIGHT
    df = results[results['id'].str.contains('studio')]

    # Split by gender
    female = df[df['gender']=='female']
    male = df[df['gender']=='male']

    # Overall
    mae_height, mape_height = calculate_mae(y_pred=df['median_est_height_cm'], y_true=df['act_height_cm'])

    turk_height_resultsdict['Turk: studio']['overall']['mae'] = mae_height
    turk_height_resultsdict['Turk: studio']['overall']['mape'] = mape_height

    # Male
    mae_height, mape_height = calculate_mae(y_pred=male['median_est_height_cm'], y_true=male['act_height_cm'])

    turk_height_resultsdict['Turk: studio']['male']['mae'] = mae_height
    turk_height_resultsdict['Turk: studio']['male']['mape'] = mape_height

    # Female
    mae_height, mape_height = calculate_mae(y_pred=female['median_est_height_cm'], y_true=female['act_height_cm'])

    turk_height_resultsdict['Turk: studio']['female']['mae'] = mae_height
    turk_height_resultsdict['Turk: studio']['female']['mape'] = mape_height

    turk_weight_results = create_summary_table(turk_experiments, turk_weight_resultsdict, units='kg')
    turk_height_results = create_summary_table(turk_experiments, turk_height_resultsdict, units='cm')

    return turk_weight_results, turk_height_results

def main():

    time_stamp = str(round(time.time(), 0))

    yaml_config = '../XX Data/config.yaml'
    inputs = get_config_inputs(yaml_config)
    qualtrics_api_token = inputs['qualtrics_api_token']
    survey_url = inputs['qualtrics_survey_url']
    qsf_file = inputs['qsf_root_file']
    lookup_location = inputs['lookup_location']
    out_path = inputs['out_path']

    df = start_and_obtain_qualtrics_export(survey_url, qualtrics_api_token, out_path, time_stamp)
    images, qids, export_tags = extract_questions(df, qsf_file)
    results = merge_questions_and_lookup(df, images, qids, export_tags, lookup_location)
    results.to_csv(f'../XX Data/turk_results/turk_results_{time_stamp}.csv')
    #turk_weight_results, turk_height_results = generate_accuracies(results)

    #turk_weight_results.to_csv(out_path+'/analysed_results/weight_'+time_stamp+'.csv')
    #turk_height_results.to_csv(out_path+'/analysed_results/height_'+time_stamp+'.csv')

    # Validate if anyone failed catch trials and remove- drop the row 

    # Also need to validate who gets paid

if __name__ == "__main__":
    main()
