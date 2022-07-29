import pickle
import trimesh
import math
import json

import json_skeleton

import openmesh as om
import numpy as np
import statsmodels.api as sm

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_absolute_percentage_error

def calculate_mae(X, Y):
    X = sm.add_constant(X)
    model = sm.OLS(Y,X)
    regression_results = model.fit()
    y_pred = regression_results.predict(X) # Model values of the thing we're predicting
    regression_mae = round(mean_absolute_error(Y, y_pred), 3)
    regression_mae_perc = round(100*mean_absolute_percentage_error(Y, y_pred), 2)

    
    print(f'Intercept = {regression_results.params[0]}')
    print(f'Coefficient = {regression_results.params[1]}')
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

def main():

	csv_results_location = '../XX Data/results/hw_13.07.22'
	df = import_and_merge_gender_results_files(csv_results_location)

	mae_height, mape_height = calculate_mae(df['est_height_cm'], df['height_cm'])

	intercept, coef1 =  get_linear_coefs(df['est_height_cm'], df['height_cm'])
	
	fig = px.scatter(df, x="est_height_cm", y="height_cm", color='gender_identity', hover_data=['id'], title = 'Scatter of Estimated vs. Actual Heights')
	fig.update_yaxes(rangemode="tozero")
	fig.update_xaxes(rangemode="tozero")
	fig.add_shape(type='line',
	                x0=0,
	                y0=intercept,
	                x1=200, # CHANGE to be a value that is near the end of the xaxis 
	                y1=intercept+(200*coef1), 
	                line=dict(color='Green',),
	                xref='x',
	                yref='y'
	)
	fig.update_traces(marker=dict(size=2))
	fig.show()

	return None

if __name__ == "__main__":
    main()
