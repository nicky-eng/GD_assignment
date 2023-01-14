import glob
import os
from io import BytesIO
import sys

from flask import Flask, jsonify, send_file
import pyarrow.parquet as pq
import pandas as pd
from pandasql import sqldf


app = Flask(__name__)

data_files_path = './faa_data'

debug = True


# This to load the correct data when running the python test script.
if len(sys.argv) > 1:
    if sys.argv[1] == 'load_test_data':
        data_files_path = './test_data'
        debug = False

data_files = glob.glob(os.path.join(data_files_path,'*.parquet'))

data = {}

for file in data_files:
    df = pq.read_table(file).to_pandas()
    data[os.path.basename(file)] = df

df1 = data['aircraft_models.parquet']
df2 = data['aircraft.parquet']

# Dataframe names for SQL queries endpoint
aircraft_models = df1
aircraft = df2
airports = data['airports.parquet']
carriers = data['carriers.parquet']
flights = data['flights.parquet'] 

active_aircraft = df2[df2['status_code'] == 'A']

active_aircraft_models = pd.merge(active_aircraft[['aircraft_serial', 'name',
        'county', 'state', 'aircraft_model_code']], df1[['manufacturer',
        'model', 'seats','aircraft_model_code']], on='aircraft_model_code')


@app.route('/data_sets')
def get_data_sets():
    """Endpoint through which clients can get information about the loaded data
    sets returning: Name of the data file, list of columns and, total number
    of rows.
    """
    response_data = []
    for file, df in data.items():
        response_data.append({
            'file_name': file,
            'name_of_columns': df.columns.tolist(),
            'num_rows': len(df),
        })
    return jsonify(response_data)


@app.route('/aircraft_models')
def get_aircraft_models():
    """Endpoint, which the client can call with no parameters and that will
    return all known aircraft models, their manufacturer and number of seats.
    """
    known_aircraft_models = []
    for _, row in aircraft_models.iterrows():
        known_aircraft_models.append({
            'aircraft_model': row['model'],
            'manufacturer': row['manufacturer'],
            'number_of_seats': row['seats'],
        })
    return jsonify(known_aircraft_models)


@app.route('/active/<manufacturer>/<model>')
def get_active_manufacturer_model(manufacturer, model):
    """Endpoint, which the client can call with two parameters: aircraft
    manufacturer, aircraft model. Returns all active aircrafts of the selected
    model and manufacturer. For each aircraft it returns: manufacturer, model,
    number of seats, serial number, registrant name and registrant county.
    """
    model_data = {}

    # aircraft_model_code is the link
    df = data['aircraft_models.parquet']

    # this is an array with the index of the aircraft model row
    aircraft_row_index = df.loc[(df['manufacturer'] == manufacturer.upper()) 
                                & (df['model'] == model.upper())].index.values
    
    if not aircraft_row_index.size > 0:
        return {}

    aircraft_model = df.iloc[aircraft_row_index[0]]

    aircraft_model_code = aircraft_model['aircraft_model_code']

    model_data['manufacturer'] = aircraft_model['manufacturer']
    model_data['model'] = aircraft_model['model']
    model_data['number_of_seats'] = str(aircraft_model['seats'])

    df2 = data['aircraft.parquet']

    active_aircraft = df2.loc[
                    (df2['aircraft_model_code'] == aircraft_model_code)
                    & (df2['status_code'] == 'A')]

    response_data = []

    for i in range(len(active_aircraft)):
        aircraft = active_aircraft.iloc[i]
        model_data['serial_number'] = aircraft['aircraft_serial']
        model_data['registrant_name'] = aircraft['name']
        model_data['registrant_county'] = aircraft['county']
        
        response_data.append(model_data)
        
    print(response_data)
    return jsonify(response_data)


@app.route('/report')
def get_report():
    """Endpoint, which the client can call with no parameters and that will
    return summary counts of active aircraft models and their manufacturer
    by the county in which those aircrafts are registered.
    """
    df = active_aircraft_models

    report = df.groupby(['state', 'county', 'manufacturer',
                            'model']).size().reset_index(name='count')
    report = report.pivot_table(index=['state', 'county'],
                        columns=['manufacturer', 'model'], values='count')

    response_data = BytesIO(report.to_csv().encode())

    return send_file(response_data, mimetype='text/csv',
                        download_name='pivot_report.csv')


@app.route('/pivot_report_county')
def get_pivot_report_county():
    """Endpoint that returns one row for each aircraft model and its
    manufacturer and the aircraft count per county should be in a column
    dedicated to that county. If the aircraft model is not registered in the
    county, then the value is NULL.
    """
    df = active_aircraft_models
    report = pd.pivot_table(df, index=['manufacturer', 'model'],
                            columns=['state', 'county'], fill_value='NULL',
                            values='aircraft_serial', aggfunc='count')
    
    response_data = BytesIO(report.to_csv().encode())

    return send_file(response_data, mimetype='text/csv',
                        download_name='pivot_report.csv')


@app.route('/pivot_report_state')
def get_pivot_report_state():
    """Same as get_pivot_report_county() endpoint but grouping by state instead
    of by county, to look like the expample output in the assignment.
    """
    df = active_aircraft_models
    report = pd.pivot_table(df, index=['manufacturer', 'model'],
                            columns=['state'], fill_value='NULL',
                            values='aircraft_serial', aggfunc='count')

    response_data = BytesIO(report.to_csv().encode())
    
    return send_file(response_data, mimetype='text/csv',
                        download_name=f'pivot_report_state.csv')


@app.route('/sql/<query>')
def sql(query):
    """Endpoint through which clients can submit SQL to run on top of the
    FAA data.
    """
    report = sqldf(query, globals())

    response_data = BytesIO(report.to_csv().encode())

    return send_file(response_data, mimetype='text/csv',
                        download_name='sql_report.csv')


if __name__ == "__main__":
    app.run(port=5000)