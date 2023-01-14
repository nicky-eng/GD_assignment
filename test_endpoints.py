import subprocess
import requests
import time
import io
import csv


# Start the Flask API using subprocess with test data files.
api_process = subprocess.Popen(['python', 'app.py', 'load_test_data'])

# Allow time for the server to start.
time.sleep(3)

# The tests are wrapped in a try-except block to make sure the Flask
# development server will terminate even if tests fail.
try:
    response = requests.get('http://localhost:5000/data_sets')
    assert response.json()[0]['num_rows'] == 1000


    response = requests.get('http://localhost:5000/aircraft_models')
    assert response.json()[9]['aircraft_model'] == 'V35B'


    # Tets endpoint with and active aircraft as parameter
    response = requests.get('http://localhost:5000/active/beech/v35b')
    assert response.json()[0]['number_of_seats'] == '6'


    # Test endpoint with inactive aircraft
    response = requests.get('http://localhost:5000/active/BOEGER BOGIE M/SKYLER J1')
    assert len(response.json()) ==	0


    # Test endpoint with inexistant aircraft
    response = requests.get('http://localhost:5000/active/no_a_real/aircraft')
    assert len(response.json()) ==	0


    response = requests.get('http://localhost:5000/pivot_report_county')
    with io.StringIO(response.text) as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i == 3:
                assert row[1] == 'V35B'
                assert row[4] == '1.0'


    response = requests.get('http://localhost:5000/pivot_report_state')
    with io.StringIO(response.text) as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i == 1:
                assert row[1] == 'V35B'
                assert row[4] == '1.0'


    response = requests.get('http://localhost:5000/sql/SELECT aircraft.state, aircraft.status_code, aircraft_models.model FROM aircraft INNER JOIN aircraft_models ON aircraft.aircraft_model_code=aircraft_models.aircraft_model_code')
    with io.StringIO(response.text) as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i == 5:
                assert row[3] == 'V35B'
                assert row[1] == 'TX'


    print('***ALL TESTS PASSED SUCCESSFULLY***')

    # Stop the api.
    api_process.terminate()

except:
    print('***SOME TESTS FAILED***')
    api_process.terminate()