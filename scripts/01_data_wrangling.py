"""Prepare launch outcomes and model inputs.

Based on IBM Skills Network SpaceX labs. See ATTRIBUTION.md and SOURCES.json.
"""
from pathlib import Path
import os
import matplotlib
matplotlib.use('Agg')
from IPython.display import display
HERE=Path(__file__).resolve().parents[1]
DATA=HERE/'data'
OUT=HERE/'results'/'01_wrangling'
OUT.mkdir(parents=True,exist_ok=True)
os.chdir(OUT)

# Pandas is a software library written for the Python programming language for data manipulation and analysis.
import pandas as pd
#NumPy is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays
import numpy as np

df=pd.read_csv(DATA/'dataset_part_1.csv')
df.head(10)

df.isnull().sum()/len(df)*100

df.dtypes

launch_site_counts=df['LaunchSite'].value_counts()
launch_site_counts

orbit_counts=df['Orbit'].value_counts()
orbit_counts

landing_outcomes=df['Outcome'].value_counts()
landing_outcomes

for i,outcome in enumerate(landing_outcomes.keys()):
    print(i,outcome)

bad_outcomes=set(landing_outcomes.keys()[[1,3,5,6,7]])
bad_outcomes

landing_class=[0 if outcome in bad_outcomes else 1 for outcome in df['Outcome']]

df['Class']=landing_class
df[['Class']].head(8)

df.head(5)

df["Class"].mean()

import json
assert len(df)==90
assert len(df['Class'])==len(df)
reference=pd.read_csv(DATA/'dataset_part_2.csv')
assert df['FlightNumber'].equals(reference['FlightNumber'])
assert df['Class'].equals(reference['Class'])
assert df['Class'].equals(df['Outcome'].str.startswith('True').astype(int))
df.to_csv(OUT/'dataset_part_2.derived.csv',index=False)
result={'rows':len(df),'successes':int(df['Class'].sum()),'success_rate':float(df['Class'].mean()),'official_Class_column_matches_all_rows':True,'site_counts':launch_site_counts.to_dict(),'bad_outcomes':sorted(bad_outcomes)}
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
