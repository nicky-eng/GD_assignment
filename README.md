> This assignment has been modified after initial delivery to incorporate
dockerization and fix one endpoint. To inspect orginal delivery, checkout
commit d5e678c7q.

# Simple Flight Data Service

A simple Flask API to explore data from the FAA. All data sets are loaded to
the sevice on startup. Tetsing is provided via python script, not using any
testing framework.

# Table of Contents

1. [Cloning the repo](#clone-the-repo)
2. [Running in Docker](#running-in-docker)
3. [Running locally](#running-locally)
4. [API Endpoints](#api-endpoints-usage)

> All CLI commands are for Unix OS

# Clone the repo

`git clone https://github.com/nicky-eng/GD_assignment.git`

`cd GD_assignment`

# Running in Docker

## Running the tests

`sudo docker build -f Dockerfile_testing -t test_gd .`

`sudo docker run test_gd`

## Running the app

`sudo docker build -t gd_app .`

`sudo docker run -p 5000:5000 gd_app`

# Running locally

## Create Virtual Environment and activate

> Python version for venv should be 3.6 or higher.

`python -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

## Testing endpoints

To test endpoints run the following command: `python test_endpoints.py`

## Launching the API in the development server

`python app.py`

# API Endpoints usage:

## Data sets endpoint
Returns a json with information about loaded data sets.


Request example: http://localhost:5000/data_sets

## Aircraft models endpoint
Returns a json with all aircraft models in the data set.


Request example: http://localhost:5000/aircraft_models

## Active aircraft model endpoint
Given manufacturer and model, returns all active aircraft of such. The parameters
are case insensitive.


Request format: http://localhost:5000/active/[manufacturer]/[model]

Request example: http://localhost:5000/active/BOEGER%20BOGIE%20M/SKYLER%20J1

##  Report endpoint
Returns a csv file with a summary count of active aircraft by county.


Request example: http://localhost:5000/report

## Pivot report by county
Returns a csv file with a pivot table summary count of active aircraft by county.


Request example: http://localhost:5000/pivot_report_county

## Pivot report by state
Returns a csv file with a pivot table summary count of active aircraft by state.


Request example: http://localhost:5000/pivot_report_state

## SQL query 
Returns a csv file with the result of a submitted SQL query.

Request format: http://localhost:5000/sql/[query]

Request example: http://localhost:5000/sql/SELECT%20aircraft.state,%20aircraft.status_code,%20aircraft_models.model%20FROM%20aircraft





