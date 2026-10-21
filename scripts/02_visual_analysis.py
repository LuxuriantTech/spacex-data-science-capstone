"""Explore launch sites, payloads, orbits and yearly trends.

Based on IBM Skills Network SpaceX labs. See ATTRIBUTION.md and SOURCES.json.
"""
from pathlib import Path
import os
import matplotlib
matplotlib.use('Agg')
from IPython.display import display
HERE=Path(__file__).resolve().parents[1]
DATA=HERE/'data'
OUT=HERE/'results'/'02_eda_visualization_v2'
OUT.mkdir(parents=True,exist_ok=True)
os.chdir(OUT)

# Save each plotted figure for portable command-line reproduction.
_figure_number=0
def save_current_figure():
    global _figure_number
    import matplotlib.pyplot as plt
    _figure_number+=1
    plt.savefig(OUT/f'figure_{_figure_number:02d}.png',dpi=150)
    plt.close()

# Load the launch data for the plots.
import pandas as pd
#NumPy is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays
import numpy as np
# Matplotlib is a plotting library for python and pyplot gives us a MatLab like plotting framework. We will use this in our plotter function to plot data.
import matplotlib.pyplot as plt
#Seaborn is a Python data visualization library based on matplotlib. It provides a high-level interface for drawing attractive and informative statistical graphics
import seaborn as sns

df=pd.read_csv(DATA/'dataset_part_2.csv')
df.head(5)

g=sns.catplot(y='PayloadMass',x='FlightNumber',hue='Class',data=df,height=4,aspect=2.4)
g.ax.set_xticks(list(range(0,len(df),10)),labels=df['FlightNumber'].iloc[::10].astype(str))
plt.xlabel('Flight number');plt.ylabel('Payload mass (kg)');plt.tight_layout();save_current_figure()

sns.catplot(x='FlightNumber',y='LaunchSite',hue='Class',data=df,height=4,aspect=2.4)
plt.xlabel('Flight number');plt.ylabel('Launch site');plt.tight_layout();save_current_figure()

sns.catplot(x='PayloadMass',y='LaunchSite',hue='Class',data=df,height=4,aspect=2.4)
plt.xlabel('Payload mass (kg)');plt.ylabel('Launch site');plt.tight_layout();save_current_figure()

orbit_summary=df.groupby('Orbit')['Class'].agg(['size','sum','mean'])
orbit_summary['mean'].plot.bar(figsize=(9,4),ylim=(0,1),ylabel='Observed landing success rate',title='Landing success by orbit (IBM snapshot)')
plt.tight_layout();save_current_figure()
display(orbit_summary)

sns.catplot(x='FlightNumber',y='Orbit',hue='Class',data=df,height=5,aspect=2)
plt.xlabel('Flight number');plt.ylabel('Orbit');plt.tight_layout();save_current_figure()

sns.catplot(x='PayloadMass',y='Orbit',hue='Class',data=df,height=5,aspect=2)
plt.xlabel('Payload mass (kg)');plt.ylabel('Orbit');plt.tight_layout();save_current_figure()

# A function to Extract years from the date 
year=[]
def Extract_year(date):
    for i in df["Date"]:
        year.append(i.split("-")[0])
    return year
    

df['Year']=Extract_year(df['Date'])
yearly_summary=df.groupby('Year')['Class'].agg(['size','sum','mean'])
yearly_summary['mean'].plot(marker='o',figsize=(9,4),ylim=(0,1),ylabel='Observed landing success rate',title='Yearly landing outcome trend (IBM snapshot)')
plt.tight_layout();save_current_figure()
display(yearly_summary)

features = df[['FlightNumber', 'PayloadMass', 'Orbit', 'LaunchSite', 'Flights', 'GridFins', 'Reused', 'Legs', 'LandingPad', 'Block', 'ReusedCount', 'Serial']]
features.head()

features_one_hot=pd.get_dummies(features,columns=['Orbit','LaunchSite','LandingPad','Serial'])
features_one_hot.head()

features_one_hot=features_one_hot.astype('float64')
features_one_hot.head()

import json
assert features_one_hot.shape[0]==len(df)==90
assert all(str(t)=='float64' for t in features_one_hot.dtypes)
assert not features_one_hot.isna().any().any()
features_one_hot.to_csv(OUT/'dataset_part_3.derived.csv',index=False)
reference=pd.read_csv(DATA/'dataset_part_3.csv')
shared=sorted(set(reference.columns)&set(features_one_hot.columns))
assert np.allclose(reference[shared],features_one_hot[shared])
orbit_summary.to_csv(OUT/'orbit_summary.csv');yearly_summary.to_csv(OUT/'yearly_summary.csv')
site_summary=df.groupby('LaunchSite')['Class'].agg(['size','sum','mean'])
display(site_summary)
result={'rows':len(df),'features_generated':features_one_hot.shape[1],'official_reference_features':reference.shape[1],'common_features_verified':len(shared),'difference_explanation':'Current pandas retains boolean inputs as 3 numeric columns; official precomputed file one-hot encodes them into 6 columns. Both encode the same observed booleans.','max_payload_VAFB':float(df.loc[df['LaunchSite']=='VAFB SLC 4E','PayloadMass'].max()),'interpretation':'Associations are descriptive; site, orbit, payload and time are confounded. Small orbit counts limit rate comparisons.'}
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
