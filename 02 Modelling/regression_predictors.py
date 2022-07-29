import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from scipy import stats
import seaborn as sns

''' 
Functions to support baseline regression predictor model for regressing weight (dependent variable) upon height (independent variable).

Author: Sarah Barrington
Date: 30th May 2022

'''

def convert_height(cm):
    ft_raw = cm/30.48
    inch_raw = ft_raw*12
    inch = inch_raw%12
    ft = math.floor(ft_raw)
    inch = round(inch, 2)
    
    return ft, inch

def convert_weight(kg):
    lbs = round(kg*2.20462, 2)

    return lbs

def return_max_min_ID(df, var, max=True):
    if max:
        ID = df.iloc[np.argmax(var)]['Participant ID']

    else:
        ID = df.iloc[np.argmin(var)]['Participant ID']

    return int(ID)

def summarise(df):
    '''Summary function to review dataset prior to modelling
    '''
    print('---DATA COLLECTION SUMMARY---\n')
    heights = df['Height (cm)']
    weights = df['Weight (kg)']
    ipds = df['IPD']
    
    max_height = heights.max()
    min_height = heights.min()
    
    max_weight = weights.max()
    min_weight = weights.min()
    
    max_ipd = ipds.max()
    min_ipd = ipds.min()

    n = len(df['Participant ID'])
    h_range = round(max_height - min_height, 2)
    w_range = round(max_weight - min_weight, 2)
    i_range = round(max_ipd - min_ipd, 2)

    print(f'Number of participants successfully collected: {n}\n')

    print('---Heights---')
    print(f'Range: {h_range}cm')
    print(f'Mean: {round(np.mean(heights), 3)}, mode {stats.mode(heights)[0]}, median: {np.median(heights)}')
    print(f'Tallest: {max_height}, {convert_height(max_height)[0]}ft {convert_height(max_height)[1]}in, (ID: 00{return_max_min_ID(df, heights)})')
    print(f'shortest: {min_height}, {convert_height(min_height)[0]}ft {convert_height(min_height)[1]}in, (ID: 00{return_max_min_ID(df, heights, max=False)})\n')

    print('---Weights---')
    print(f'Range: {w_range}kg')
    print(f'Mean: {round(np.mean(weights), 3)}, mode {stats.mode(weights)[0]}, median: {np.median(weights)}')
    print(f'Largest: {max_weight}kg, {convert_weight(max_weight)}lbs (ID: 00{return_max_min_ID(df, weights)})')
    print(f'Smallest: {min_weight}kg, {convert_weight(min_weight)}lbs (ID: 00{return_max_min_ID(df, weights, max=False)})')
    print(' ')
    
    print('---IPDs---')
    print(f'Range: {i_range}cm')
    print(f'Mean: {round(np.mean(ipds), 6)}, mode {stats.mode(ipds)[0]}, median: {np.median(ipds)}')
    print(f'Largest: {max_ipd}cm, (ID: 00{return_max_min_ID(df, ipds)})')
    print(f'Smallest: {min_ipd}cm, (ID: 00{return_max_min_ID(df, ipds, max=False)})')

    return heights, weights, ipds, n

def plot_scatter(df, col1, col2):
    '''
    Create Plotly scatter plot of height vs. weight, 
    illustrating the initial linear regression line of best fit. 
    '''
    fig = px.scatter(df, x="Weight (kg)", y="Height (cm)", hover_data=['Participant ID'], title = 'Scatter of Weights and Heights', trendline='ols')
    fig.show()


def plot_population_comparison(var, popmean, popstd, subplot_no = 0, norm_obs = 1000, markers=False):
    sns.set_style("darkgrid")

    meanhm = np.mean(var)
    stdhm = np.std(var)
    
    np.random.seed(1)

    # CREATE dataframe with imputation for study bins
    data = pd.DataFrame({'Population':np.random.normal(popmean, popstd, norm_obs), 'Study':np.nan})
    data['Study'].iloc[0:len(var)] = var

    sns.distplot(data['Study'], ax = ax[subplot_no], label = 'Study')
    plt.xlabel("Height (cm)")
    if markers:
        plt.axvline(meanhm)
    sns.distplot(data['Population'], ax=ax[subplot_no], label = 'Population')
    if markers:
        plt.axvline(meanpopm)

    return None

def ttest(data):
    '''Generic t-test of study vs. population data, assuming un-equal variances
    '''
    result = stats.ttest_ind(data['Study'], data['Population'], 
                      equal_var=False)
    if result.pvalue > 0.05:
        print(f'pval = {round(result.pvalue, 6)}, distributions can be assumed the same')
    else:
        print(f'pval = {round(result.pvalue, 6)}, distributions cannot be assumed the same')

    return None

def create_raw_mae_table(se_mean, 
    mean_mae_perc, 
    mean_mae, 
    male_mean_mae_perc, 
    male_mean_mae, 
    nonmale_mean_mae_perc, 
    nonmale_mean_mae, 
    se_height_regression, 
    height_regression_mae_perc, 
    height_regression_mae, r2_height, r2_height_gender, male_mean_paper_mae_perc, male_mean_paper_mae,
    nonmale_mean_paper_mae_perc, nonmale_mean_paper_mae, se_height_gender_regression, gender_regression_mae_perc, gender_regression_mae):

    results = pd.DataFrame(columns=['Mean Absolute Error (%)', 'Mean Absolute Error (kg)', 'Standard Error: Weight', 'R^2 Value'], index=['Gender specific mean (overall, true data)', 'Gender specific mean (male, true data)', 'Gender specific mean (non-male, true data)','Height Regression', 'Height Regression (gendered)', 'Gender specific mean (male, from paper)','Gender specific mean (non-male, from paper)', '3D Volume Estimation', 'Forensic Expert', 'General Public'])

    results.loc['Gender specific mean (overall, true data)', 'Standard Error: Weight'] = se_mean
    results.loc['Gender specific mean (overall, true data)', 'Mean Absolute Error (%)'] = mean_mae_perc
    results.loc['Gender specific mean (overall, true data)', 'Mean Absolute Error (kg)'] = mean_mae

    results.loc['Gender specific mean (male, true data)', 'Mean Absolute Error (%)'] = male_mean_mae_perc
    results.loc['Gender specific mean (male, true data)', 'Mean Absolute Error (kg)'] = male_mean_mae

    results.loc['Gender specific mean (non-male, true data)', 'Mean Absolute Error (%)'] = nonmale_mean_mae_perc
    results.loc['Gender specific mean (non-male, true data)', 'Mean Absolute Error (kg)'] = nonmale_mean_mae

    results.loc['Height Regression', 'Standard Error: Weight'] = se_height_regression
    results.loc['Height Regression', 'Mean Absolute Error (%)'] = height_regression_mae_perc
    results.loc['Height Regression', 'Mean Absolute Error (kg)'] = height_regression_mae
    results.loc['Height Regression', 'R^2 Value'] = r2_height

    results.loc['Height Regression (gendered)', 'Standard Error: Weight'] = se_height_gender_regression
    results.loc['Height Regression (gendered)', 'Mean Absolute Error (%)'] = gender_regression_mae_perc
    results.loc['Height Regression (gendered)', 'Mean Absolute Error (kg)'] = gender_regression_mae
    results.loc['Height Regression (gendered)', 'R^2 Value'] = r2_height_gender

    results.loc['Gender specific mean (male, from paper)', 'Mean Absolute Error (%)'] = male_mean_paper_mae_perc
    results.loc['Gender specific mean (male, from paper)', 'Mean Absolute Error (kg)'] = male_mean_paper_mae

    results.loc['Gender specific mean (non-male, from paper)', 'Mean Absolute Error (%)'] = nonmale_mean_paper_mae_perc
    results.loc['Gender specific mean (non-male, from paper)', 'Mean Absolute Error (kg)'] = nonmale_mean_paper_mae

    results = results.sort_values(by='Mean Absolute Error (%)', ascending=True)

    return results


def create_MAE_summary_table_individual_inputs(male_mean_mae_perc,
    nonmale_mean_mae_perc,
    mean_mae_perc,
    male_mean_mae,
    nonmale_mean_mae,
    mean_mae,
    male_mean_paper_mae_perc,
    nonmale_mean_paper_mae_perc,
    male_mean_paper_mae,
    nonmale_mean_paper_mae,
    male_regr_mae_perc,
    nonmale_regr_mae_perc,
    height_regression_mae_perc,
    male_regr_mae,
    nonmale_regr_mae,
    height_regression_mae,
    gender_regression_mae_perc,
    male_regr_gender_mae_perc,
    nonmale_regr_gender_mae_perc,
    gender_regression_mae,
    male_regr_gender_mae,
    nonmale_regr_gender_mae,
    nonmale_3d_gender_mae,
    male_3d_gender_mae,
    overall_3d_gender_mae,
    nonmale_3d_gender_mae_perc,
    male_3d_gender_mae_perc,
    overall_3d_gender_mae_perc
    ):

    columns = [['Male','Male', 
            'Female','Female',
            'Overall', 'Overall', 
           ],
        ['MAPE (%)','MAE (kg)',
         'MAPE (%)','MAE (kg)',
         'MAPE (%)','MAE (kg)',#, 
            #'Standard Error','Standard Error','Standard Error', 
            #'R^2 Value','R^2 Value','R^2 Value'
           ]]
    tuples = list(zip(*columns))
    multicol = pd.MultiIndex.from_tuples(tuples)

    rows = ['Gender specific mean (true data)',
            'Height Regression', 
            'Height Regression (gendered)', 
            'Gender specific mean (from paper)',
            '3D Volume Estimation * 985', 
            'Forensic Experts', 
            'General Public']

    results_gendered = pd.DataFrame(columns=multicol, index=rows)


    results_gendered.loc['Gender specific mean (true data)', ('Male', 'MAPE (%)')]= male_mean_mae_perc
    results_gendered.loc['Gender specific mean (true data)', ('Female', 'MAPE (%)')] = nonmale_mean_mae_perc
    results_gendered.loc['Gender specific mean (true data)', ('Overall', 'MAPE (%)')] = mean_mae_perc

    results_gendered.loc['Gender specific mean (true data)', ('Male', 'MAE (kg)')] = male_mean_mae
    results_gendered.loc['Gender specific mean (true data)', ('Female', 'MAE (kg)')] = nonmale_mean_mae
    results_gendered.loc['Gender specific mean (true data)', ('Overall', 'MAE (kg)')] = mean_mae

    results_gendered.loc['Gender specific mean (from paper)', ('Male', 'MAPE (%)')] = male_mean_paper_mae_perc
    results_gendered.loc['Gender specific mean (from paper)', ('Female', 'MAPE (%)')] = nonmale_mean_paper_mae_perc

    results_gendered.loc['Gender specific mean (from paper)', ('Male', 'MAE (kg)')] = male_mean_paper_mae
    results_gendered.loc['Gender specific mean (from paper)', ('Female', 'MAE (kg)')] = nonmale_mean_paper_mae

    results_gendered.loc['Height Regression', ('Male', 'MAPE (%)')] = male_regr_mae_perc
    results_gendered.loc['Height Regression', ('Female', 'MAPE (%)')] = nonmale_regr_mae_perc
    results_gendered.loc['Height Regression', ('Overall', 'MAPE (%)')] = height_regression_mae_perc

    results_gendered.loc['Height Regression', ('Male', 'MAE (kg)')] = male_regr_mae
    results_gendered.loc['Height Regression', ('Female', 'MAE (kg)')] = nonmale_regr_mae
    results_gendered.loc['Height Regression', ('Overall', 'MAE (kg)')] = height_regression_mae

    results_gendered.loc['Height Regression (gendered)', ('Overall', 'MAPE (%)')] = gender_regression_mae_perc
    results_gendered.loc['Height Regression (gendered)', ('Male', 'MAPE (%)')] = male_regr_gender_mae_perc
    results_gendered.loc['Height Regression (gendered)', ('Female', 'MAPE (%)')] = nonmale_regr_gender_mae_perc

    results_gendered.loc['Height Regression (gendered)', ('Overall', 'MAE (kg)')] = gender_regression_mae
    results_gendered.loc['Height Regression (gendered)', ('Male', 'MAE (kg)')] = male_regr_gender_mae
    results_gendered.loc['Height Regression (gendered)', ('Female', 'MAE (kg)')] = nonmale_regr_gender_mae

    results_gendered.loc['3D Volume Estimation * 985', ('Female', 'MAE (kg)')] = nonmale_3d_gender_mae
    results_gendered.loc['3D Volume Estimation * 985', ('Male', 'MAE (kg)')] = male_3d_gender_mae
    results_gendered.loc['3D Volume Estimation * 985', ('Overall', 'MAE (kg)')] = overall_3d_gender_mae
    
    results_gendered.loc['3D Volume Estimation * 985', ('Female', 'MAPE (%)')] = nonmale_3d_gender_mae_perc
    results_gendered.loc['3D Volume Estimation * 985', ('Male', 'MAPE (%)')] = male_3d_gender_mae_perc
    results_gendered.loc['3D Volume Estimation * 985', ('Overall', 'MAPE (%)')] = overall_3d_gender_mae_perc


    results_gendered = results_gendered.sort_values(by=[('Male', 'MAPE (%)')], ascending=True)

    results_gendered.loc[:,('Male', 'MAPE (%)')] = results_gendered.loc[:,('Male', 'MAPE (%)')].astype(str)+'%'
    results_gendered.loc[:,('Female', 'MAPE (%)')] = results_gendered.loc[:,('Female', 'MAPE (%)')].astype(str)+'%'
    results_gendered.loc[:,('Overall', 'MAPE (%)')] = results_gendered.loc[:,('Overall', 'MAPE (%)')].astype(str)+'%'
    
    results_gendered = results_gendered.replace('nan%', 'NaN')

    return results_gendered



def create_MAE_summary_table(listofdicts):
    '''
    listofdicts:    list of dictionaries to feed in containing experiment, 
                    gender (male, female, overall), MAE and MAPE

    '''

    columns = [['Male','Male', 
            'Female','Female',
            'Overall', 'Overall', 
           ],
        ['MAPE (%)','MAE (kg)',
         'MAPE (%)','MAE (kg)',
         'MAPE (%)','MAE (kg)',#, 
            #'Standard Error','Standard Error','Standard Error', 
            #'R^2 Value','R^2 Value','R^2 Value'
           ]]
    tuples = list(zip(*columns))
    multicol = pd.MultiIndex.from_tuples(tuples)


    rows = ['Gender specific mean (true data)',
            'Height Regression', 
            'Height Regression (gendered)', 
            'Gender specific mean (from paper)',
            '3D Volume Estimation * 985', 
            'Forensic Experts', 
            'General Public']

    results_gendered = pd.DataFrame(columns=multicol, index=rows)


    results_gendered.loc['Gender specific mean (true data)', ('Male', 'MAPE (%)')]= male_mean_mae_perc
    results_gendered.loc['Gender specific mean (true data)', ('Female', 'MAPE (%)')] = nonmale_mean_mae_perc
    results_gendered.loc['Gender specific mean (true data)', ('Overall', 'MAPE (%)')] = mean_mae_perc

    results_gendered.loc['Gender specific mean (true data)', ('Male', 'MAE (kg)')] = male_mean_mae
    results_gendered.loc['Gender specific mean (true data)', ('Female', 'MAE (kg)')] = nonmale_mean_mae
    results_gendered.loc['Gender specific mean (true data)', ('Overall', 'MAE (kg)')] = mean_mae

    results_gendered.loc['Gender specific mean (from paper)', ('Male', 'MAPE (%)')] = male_mean_paper_mae_perc
    results_gendered.loc['Gender specific mean (from paper)', ('Female', 'MAPE (%)')] = nonmale_mean_paper_mae_perc

    results_gendered.loc['Gender specific mean (from paper)', ('Male', 'MAE (kg)')] = male_mean_paper_mae
    results_gendered.loc['Gender specific mean (from paper)', ('Female', 'MAE (kg)')] = nonmale_mean_paper_mae

    results_gendered.loc['Height Regression', ('Male', 'MAPE (%)')] = male_regr_mae_perc
    results_gendered.loc['Height Regression', ('Female', 'MAPE (%)')] = nonmale_regr_mae_perc
    results_gendered.loc['Height Regression', ('Overall', 'MAPE (%)')] = height_regression_mae_perc

    results_gendered.loc['Height Regression', ('Male', 'MAE (kg)')] = male_regr_mae
    results_gendered.loc['Height Regression', ('Female', 'MAE (kg)')] = nonmale_regr_mae
    results_gendered.loc['Height Regression', ('Overall', 'MAE (kg)')] = height_regression_mae

    results_gendered.loc['Height Regression (gendered)', ('Overall', 'MAPE (%)')] = gender_regression_mae_perc
    results_gendered.loc['Height Regression (gendered)', ('Male', 'MAPE (%)')] = male_regr_gender_mae_perc
    results_gendered.loc['Height Regression (gendered)', ('Female', 'MAPE (%)')] = nonmale_regr_gender_mae_perc

    results_gendered.loc['Height Regression (gendered)', ('Overall', 'MAE (kg)')] = gender_regression_mae
    results_gendered.loc['Height Regression (gendered)', ('Male', 'MAE (kg)')] = male_regr_gender_mae
    results_gendered.loc['Height Regression (gendered)', ('Female', 'MAE (kg)')] = nonmale_regr_gender_mae

    results_gendered.loc['3D Volume Estimation * 985', ('Female', 'MAE (kg)')] = nonmale_3d_gender_mae
    results_gendered.loc['3D Volume Estimation * 985', ('Male', 'MAE (kg)')] = male_3d_gender_mae
    results_gendered.loc['3D Volume Estimation * 985', ('Overall', 'MAE (kg)')] = overall_3d_gender_mae
    
    results_gendered.loc['3D Volume Estimation * 985', ('Female', 'MAPE (%)')] = nonmale_3d_gender_mae_perc
    results_gendered.loc['3D Volume Estimation * 985', ('Male', 'MAPE (%)')] = male_3d_gender_mae_perc
    results_gendered.loc['3D Volume Estimation * 985', ('Overall', 'MAPE (%)')] = overall_3d_gender_mae_perc


    results_gendered = results_gendered.sort_values(by=[('Male', 'MAPE (%)')], ascending=True)

    results_gendered.loc[:,('Male', 'MAPE (%)')] = results_gendered.loc[:,('Male', 'MAPE (%)')].astype(str)+'%'
    results_gendered.loc[:,('Female', 'MAPE (%)')] = results_gendered.loc[:,('Female', 'MAPE (%)')].astype(str)+'%'
    results_gendered.loc[:,('Overall', 'MAPE (%)')] = results_gendered.loc[:,('Overall', 'MAPE (%)')].astype(str)+'%'
    
    results_gendered = results_gendered.replace('nan%', 'NaN')

    return results_gendered

