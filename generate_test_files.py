import glob
import os
import pandas as pd

import pyarrow.parquet as pq


data_files = glob.glob('./faa_data/*.parquet')

data = {}


for file in data_files:
    df = pq.read_table(file).to_pandas()
    data[os.path.basename(file)] = df
    df.to_csv(f'{os.path.basename(file)}.csv')


aircraft_models = data['aircraft_models.parquet']
aircraft = data['aircraft.parquet']
airports = data['airports.parquet']
carriers = data['carriers.parquet']
flights = data['flights.parquet'] 


# Create aircraft.parquet
save_path = './test_data'
test_aircraft = aircraft.head(5)

test_aircraft.to_parquet(os.path.join(save_path, 'aircraft.parquet'))
test_aircraft.to_csv(os.path.join(save_path, 'aircraft.csv'))

# Create aircraft_models.parquet including the aircraft
# models in aircraft.parquet
models = []
df1 = aircraft_models.head(5)
df2 = test_aircraft

for i in range(len(df2)):
    aircraft_code = df2.iloc[i]['aircraft_model_code']
    aircraft_to_add = aircraft_models[aircraft_models[
            'aircraft_model_code'] == aircraft_code]

    df1 = pd.concat([df1, aircraft_to_add], axis = 0, ignore_index=True)  

df1.to_parquet(os.path.join(save_path, 'aircraft_models.parquet'))
df1.to_csv(os.path.join(save_path, 'aircraft_models.csv'))