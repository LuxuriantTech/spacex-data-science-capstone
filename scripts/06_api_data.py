"""Prepare the saved SpaceX API response; live enrichment is optional.

Based on IBM Skills Network SpaceX labs. See ATTRIBUTION.md and SOURCES.json.
"""
from pathlib import Path
import os
import matplotlib
matplotlib.use('Agg')
from IPython.display import display
HERE=Path(__file__).resolve().parents[1]
DATA=HERE/'data'
OUT=HERE/'results'/'06_api_partial'
OUT.mkdir(parents=True,exist_ok=True)
os.chdir(OUT)

import argparse, datetime, json
import pandas as pd
import requests
parser=argparse.ArgumentParser(description='Parse the exact IBM static launch snapshot; no enrichment is fabricated.')
parser.add_argument('--probe-live',action='store_true',help='Optional single GET with 10-second timeout; no retries or per-record enrichment')
args=parser.parse_args()
live_available=False
probe={'requested':args.probe_live,'method':'default local snapshot only','enrichment_completed':False}
if args.probe_live:
    try:
        response=requests.get('https://api.spacexdata.com/v4/launches/past',timeout=10)
        probe['http_status']=response.status_code
        live_available=response.status_code==200
    except requests.RequestException as exc:
        probe['error']=repr(exc)
(OUT/'LIVE_PROBE.json').write_text(json.dumps(probe,indent=2),encoding='utf-8')
static_json_url='https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json'

import json,hashlib
static_path=DATA/'API_call_spacex_api.json'
static_payload=json.loads(static_path.read_text())
acquisition=next(r for r in json.loads((HERE/'DATA_ACQUISITION.json').read_text()) if r['path']==str(static_path))
assert hashlib.sha256(static_path.read_bytes()).hexdigest()==acquisition['sha256']


{k:acquisition[k] for k in ['url','status','bytes','sha256']}

data=pd.json_normalize(static_payload)

data.head(5)

# Lets take a subset of our dataframe keeping only the features we want and the flight number, and date_utc.
data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]

# We will remove rows with multiple cores because those are falcon rockets with 2 extra rocket boosters and rows that have multiple payloads in a single rocket.
data = data[data['cores'].map(len)==1]
data = data[data['payloads'].map(len)==1]

# Since payloads and cores are lists of size 1 we will also extract the single value in the list and replace the feature.
data['cores'] = data['cores'].map(lambda x : x[0])
data['payloads'] = data['payloads'].map(lambda x : x[0])

# We also want to convert the date_utc to a datetime datatype and then extracting the date leaving the time
data['date'] = pd.to_datetime(data['date_utc']).dt.date

# Using the date we will restrict the dates of the launches
data = data[data['date'] <= datetime.date(2020, 11, 13)]

#Global variables 
BoosterVersion = []
PayloadMass = []
Orbit = []
LaunchSite = []
Outcome = []
Flights = []
GridFins = []
Reused = []
Legs = []
LandingPad = []
Block = []
ReusedCount = []
Serial = []
Longitude = []
Latitude = []

BoosterVersion

# Static launch JSON is real IBM data. Enrichment still requires the unavailable API.
data.to_json(OUT/'static_launch_subset.json',orient='records',date_format='iso')
(OUT/'PARTIAL.json').write_text(json.dumps({'static_launch_rows_after_template_filters':len(data),'live_available':live_available,'blocked':'Rocket, launchpad, payload and core enrichment endpoints unavailable; official dataset_part_1 is not claimed as a recreated API result.'},indent=2))
print('PARTIAL: static snapshot parsed; live enrichment was not reconstructed.')


