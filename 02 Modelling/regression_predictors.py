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

