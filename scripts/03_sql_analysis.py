"""Explore launch records with SQLite queries.

Based on IBM Skills Network SpaceX labs. See ATTRIBUTION.md and SOURCES.json.
"""
from pathlib import Path
import os
import matplotlib
matplotlib.use('Agg')
from IPython.display import display
HERE=Path(__file__).resolve().parents[1]
DATA=HERE/'data'
OUT=HERE/'results'/'03_sql_sqlite_official_variant'
OUT.mkdir(parents=True,exist_ok=True)
os.chdir(OUT)

# Use SQLite through Python's standard library.

# Run SQL queries with sqlite3 and pandas.



import csv,sqlite3
con=sqlite3.connect('spacex_local.sqlite')
cur=con.cursor()



print('SQLite version',sqlite3.sqlite_version)

import pandas as pd
df=pd.read_csv(DATA/'Spacex.csv')
df.to_sql('SPACEXTBL',con,if_exists='replace',index=False,method='multi')

con.execute('DROP TABLE IF EXISTS SPACEXTABLE');con.commit()

con.execute('CREATE TABLE SPACEXTABLE AS SELECT * FROM SPACEXTBL WHERE Date IS NOT NULL');con.commit()

query_1='SELECT DISTINCT Launch_Site FROM SPACEXTABLE ORDER BY Launch_Site'
result_1=pd.read_sql_query(query_1,con)
display(result_1)
result_1.to_csv(OUT/'task_1.csv',index=False)

query_2="SELECT * FROM SPACEXTABLE WHERE Launch_Site LIKE 'CCA%' LIMIT 5"
result_2=pd.read_sql_query(query_2,con)
display(result_2)
result_2.to_csv(OUT/'task_2.csv',index=False)

query_3="SELECT SUM(PAYLOAD_MASS__KG_) AS nasa_crs_payload_kg FROM SPACEXTABLE WHERE Customer = 'NASA (CRS)'"
result_3=pd.read_sql_query(query_3,con)
display(result_3)
result_3.to_csv(OUT/'task_3.csv',index=False)

query_4="SELECT AVG(PAYLOAD_MASS__KG_) AS mean_payload_kg FROM SPACEXTABLE WHERE Booster_Version = 'F9 v1.1'"
result_4=pd.read_sql_query(query_4,con)
display(result_4)
result_4.to_csv(OUT/'task_4.csv',index=False)

query_5="SELECT MIN(Date) AS first_successful_ground_pad_date FROM SPACEXTABLE WHERE Landing_Outcome = 'Success (ground pad)'"
result_5=pd.read_sql_query(query_5,con)
display(result_5)
result_5.to_csv(OUT/'task_5.csv',index=False)

query_6="SELECT Booster_Version FROM SPACEXTABLE WHERE Landing_Outcome = 'Success (drone ship)' AND PAYLOAD_MASS__KG_ > 4000 AND PAYLOAD_MASS__KG_ < 6000"
result_6=pd.read_sql_query(query_6,con)
display(result_6)
result_6.to_csv(OUT/'task_6.csv',index=False)

query_7='SELECT Mission_Outcome, COUNT(*) AS launches FROM SPACEXTABLE GROUP BY Mission_Outcome ORDER BY launches DESC'
result_7=pd.read_sql_query(query_7,con)
display(result_7)
result_7.to_csv(OUT/'task_7.csv',index=False)

query_8='SELECT Booster_Version, PAYLOAD_MASS__KG_ FROM SPACEXTABLE WHERE PAYLOAD_MASS__KG_ = (SELECT MAX(PAYLOAD_MASS__KG_) FROM SPACEXTABLE)'
result_8=pd.read_sql_query(query_8,con)
display(result_8)
result_8.to_csv(OUT/'task_8.csv',index=False)

query_9="SELECT substr(Date,6,2) AS month, Landing_Outcome,Booster_Version,Launch_Site FROM SPACEXTABLE WHERE substr(Date,1,4)='2015' AND Landing_Outcome = 'Failure (drone ship)'"
result_9=pd.read_sql_query(query_9,con)
display(result_9)
result_9.to_csv(OUT/'task_9.csv',index=False)

query_10="SELECT Landing_Outcome,COUNT(*) AS outcomes FROM SPACEXTABLE WHERE Date BETWEEN '2010-06-04' AND '2017-03-20' GROUP BY Landing_Outcome ORDER BY outcomes DESC"
result_10=pd.read_sql_query(query_10,con)
display(result_10)
result_10.to_csv(OUT/'task_10.csv',index=False)

import json
assert con.execute('SELECT COUNT(*) FROM SPACEXTABLE').fetchone()[0]==len(df)==101
assert int(result_3.iloc[0,0])==int(df.loc[df['Customer'].eq('NASA (CRS)'),'PAYLOAD_MASS__KG_'].sum())
assert result_5.iloc[0,0]==df.loc[df['Landing_Outcome'].eq('Success (ground pad)'),'Date'].min()
assert result_7['launches'].sum()==len(df)
assert result_9.shape[0]==len(df[df['Date'].str.startswith('2015') & df['Landing_Outcome'].eq('Failure (drone ship)')])
summary={'rows':len(df),'tasks':10,'nasa_crs_payload_kg':int(result_3.iloc[0,0]),'first_ground_pad_date':result_5.iloc[0,0],'engine':'sqlite3; official IBM SQLite variant'}
(OUT/'RESULTS.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));con.close()
