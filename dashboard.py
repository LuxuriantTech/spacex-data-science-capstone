"""Explore launch outcomes by site and payload using the IBM course dataset."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

spacex_df = pd.read_csv(HERE/'data/spacex_launch_dash.csv')
sites = sorted(spacex_df['Launch Site'].unique())
min_payload = float(spacex_df['Payload Mass (kg)'].min())
max_payload = float(spacex_df['Payload Mass (kg)'].max())
app = Dash(__name__)
app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign':'center'}),
    html.P('IBM course dataset: 56 launch records. Select a site and payload range to explore the results.'),
    html.Label('Launch site', htmlFor='site-dropdown'),
    dcc.Dropdown(id='site-dropdown', options=[{'label':'All Sites','value':'ALL'}] +
                 [{'label':s,'value':s} for s in sites], value='ALL', clearable=False),
    dcc.Graph(id='success-pie-chart'),
    html.P('Payload range (kg)'),
    dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                    marks={i:str(i) for i in range(0,10001,1000)},
                    value=[min_payload,max_payload]),
    dcc.Graph(id='success-payload-scatter-chart'),
], style={'maxWidth':'1100px','margin':'auto','padding':'24px'})

def select_site(site):
    if site != 'ALL' and site not in sites: raise ValueError('Unknown launch site')
    return spacex_df if site=='ALL' else spacex_df[spacex_df['Launch Site']==site]

@app.callback(Output('success-pie-chart','figure'), Input('site-dropdown','value'))
def get_pie_chart(entered_site):
    filtered = select_site(entered_site)
    if entered_site=='ALL':
        counts=filtered.groupby('Launch Site',as_index=False)['class'].sum()
        return px.pie(counts, values='class', names='Launch Site',
                       title='Successful landings by launch site (count)')
    counts=filtered['class'].value_counts().reindex([0,1],fill_value=0)
    return px.pie(names=['Failure','Success'],values=counts.to_list(),
                    title=f'Landing outcomes: {entered_site}',
                    color=['Failure','Success'],
                    color_discrete_map={'Failure':'#c44747','Success':'#247a68'})

@app.callback(Output('success-payload-scatter-chart','figure'),
              Input('site-dropdown','value'), Input('payload-slider','value'))
def get_scatter_chart(entered_site,payload_range):
    lower,upper=payload_range
    filtered=select_site(entered_site)
    filtered=filtered[filtered['Payload Mass (kg)'].between(lower,upper,inclusive='both')]
    fig=px.scatter(filtered,x='Payload Mass (kg)',y='class',
                    color='Booster Version Category',hover_data=['Flight Number','Launch Site'],
                    title=f'Payload and landing outcome: {entered_site}')
    fig.update_yaxes(tickvals=[0,1],ticktext=['Failure (0)','Success (1)'],range=[-0.15,1.15])
    return fig

if __name__=='__main__':
    app.run(host='127.0.0.1',port=8060,debug=False)
