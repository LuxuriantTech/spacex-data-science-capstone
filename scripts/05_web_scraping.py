"""Extract numbered launch records from the saved Wikipedia page.

Based on IBM Skills Network SpaceX labs. See ATTRIBUTION.md and SOURCES.json.
"""
from pathlib import Path
import os
import matplotlib
matplotlib.use('Agg')
from IPython.display import display
HERE=Path(__file__).resolve().parents[1]
DATA=HERE/'data'
OUT=HERE/'results'/'05_web_scraping'
OUT.mkdir(parents=True,exist_ok=True)
os.chdir(OUT)

# Parse the saved page with Beautiful Soup.

import sys

import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd

def date_time(table_cells):
    """
    This function returns the data and time from the HTML  table cell
    Input: the  element of a table data cell extracts extra row
    """
    return [data_time.strip() for data_time in list(table_cells.strings)][0:2]

def booster_version(table_cells):
    """
    This function returns the booster version from the HTML  table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=''.join([booster_version for i,booster_version in enumerate( table_cells.strings) if i%2==0][0:-1])
    return out

def landing_status(table_cells):
    """
    This function returns the landing status from the HTML table cell 
    Input: the  element of a table data cell extracts extra row
    """
    out=[i for i in table_cells.strings][0]
    return out


def get_mass(table_cells):
    mass=unicodedata.normalize("NFKD", table_cells.text).strip()
    if mass:
        mass.find("kg")
        new_mass=mass[0:mass.find("kg")+2]
    else:
        new_mass=0
    return new_mass


def extract_column_from_header(row):
    """
    This function returns the landing status from the HTML table cell 
    Input: the  element of a table data cell extracts extra row
    """
    if (row.br):
        row.br.extract()
    if row.a:
        row.a.extract()
    if row.sup:
        row.sup.extract()
        
    colunm_name = ' '.join(row.contents)
    
    # Filter the digit and empty names
    if not(colunm_name.strip().isdigit()):
        colunm_name = colunm_name.strip()
        return colunm_name    


static_url = "https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36"
}

# Use the hash-verified snapshot prepared by download_inputs.py.
import json,hashlib
acquisitions=json.loads((HERE/'DATA_ACQUISITION.json').read_text())
acquisition=next(r for r in acquisitions if r['url']==static_url)
assert acquisition['status']==200 or acquisition.get('source_mode')=='verified_cache'
html_bytes=(DATA/'wiki_oldid_1027686922.html').read_bytes()
assert hashlib.sha256(html_bytes).hexdigest()==acquisition['sha256']
print({k:acquisition[k] for k in ['url','status','source_mode','bytes','sha256']})


soup=BeautifulSoup(html_bytes,'html.parser')

soup.title.get_text()

html_tables=soup.find_all('table')
print('Number of HTML tables:',len(html_tables))

first_launch_table=html_tables[2]
print(first_launch_table.get_text(' ',strip=True)[:1800])

column_names=[]
for header in first_launch_table.find_all('th'):
    name=extract_column_from_header(header)
    if name is not None and len(name)>0:column_names.append(name)


print(column_names)

launch_dict= dict.fromkeys(column_names)

# Remove an irrelvant column
del launch_dict['Date and time ( )']

# Let's initial the launch_dict with each value to be an empty list
launch_dict['Flight No.'] = []
launch_dict['Launch site'] = []
launch_dict['Payload'] = []
launch_dict['Payload mass'] = []
launch_dict['Orbit'] = []
launch_dict['Customer'] = []
launch_dict['Launch outcome'] = []
# Added some new columns
launch_dict['Version Booster']=[]
launch_dict['Booster landing']=[]
launch_dict['Date']=[]
launch_dict['Time']=[]

extracted_row=0
for table_number,table in enumerate(soup.find_all('table','wikitable plainrowheaders collapsible')):
    for rows in table.find_all('tr'):
        flight_heading=rows.find('th',scope='row')
        if flight_heading is None:continue
        flight_number=flight_heading.get_text(strip=True)
        if not flight_number.isdigit():continue
        row=rows.find_all('td',recursive=False)
        if len(row)!=9:raise ValueError(f'Unexpected launch row width {flight_number}: {len(row)}')
        extracted_row+=1
        launch_dict['Flight No.'].append(flight_number)
        datatimelist=date_time(row[0])
        launch_dict['Date'].append(datatimelist[0].strip(','))
        launch_dict['Time'].append(datatimelist[1] if len(datatimelist)>1 else None)
        bv=booster_version(row[1])
        launch_dict['Version Booster'].append(bv or row[1].get_text(' ',strip=True))
        launch_dict['Launch site'].append(row[2].get_text(' ',strip=True))
        launch_dict['Payload'].append(row[3].get_text(' ',strip=True))
        launch_dict['Payload mass'].append(get_mass(row[4]))
        launch_dict['Orbit'].append(row[5].get_text(' ',strip=True))
        launch_dict['Customer'].append(row[6].get_text(' ',strip=True))
        launch_dict['Launch outcome'].append(row[7].get_text(' ',strip=True))
        launch_dict['Booster landing'].append(landing_status(row[8]))
print('Extracted numbered Falcon 9 launches:',extracted_row)


df= pd.DataFrame({ key:pd.Series(value) for key, value in launch_dict.items() })

assert extracted_row>0
assert all(len(v)==extracted_row for v in launch_dict.values())
assert df['Flight No.'].is_unique
assert len(df)==extracted_row
raw_numbered_rows=[row for table in soup.find_all('table','wikitable plainrowheaders collapsible') for row in table.find_all('tr') if row.find('th',scope='row') is not None and row.find('th',scope='row').get_text(strip=True).isdigit()]
assert len(raw_numbered_rows)==len(df)
assert df.iloc[0]['Date']=='4 June 2010'
assert df.iloc[0]['Time']=='18:45'
df.to_csv(OUT/'spacex_web_scraped.csv',index=False)
display(df.head());display(df.tail())
result={'rows':len(df),'first_flight':df.iloc[0]['Flight No.'],'last_flight':df.iloc[-1]['Flight No.'],'all_column_lengths_match':True,'source_revision':'1027686922','scope':'Numeric Falcon 9 flight identifiers from IBM-specified Wikipedia snapshot; no future operational inference.'}
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
