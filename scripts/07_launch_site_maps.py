"""Build launch-site maps from the IBM course data.

Based on IBM Skills Network SpaceX labs. See ATTRIBUTION.md and SOURCES.json.
"""
from pathlib import Path
import os
import matplotlib
matplotlib.use('Agg')
from IPython.display import display
HERE=Path(__file__).resolve().parents[1]
DATA=HERE/'data'
OUT=HERE/'results'/'07_folium_partial_v2'
OUT.mkdir(parents=True,exist_ok=True)
os.chdir(OUT)

# Folium already installed in isolated dependencies; urllib acquisition preserved separately.

import folium
import pandas as pd

# Import folium MarkerCluster plugin
from folium.plugins import MarkerCluster
# Import folium MousePosition plugin
from folium.plugins import MousePosition
# Import folium DivIcon plugin
from folium.features import DivIcon

spacex_df=pd.read_csv(DATA/'spacex_launch_geo.csv')

# Select relevant sub-columns: `Launch Site`, `Lat(Latitude)`, `Long(Longitude)`, `class`
spacex_df = spacex_df[['Launch Site', 'Lat', 'Long', 'class']]
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_df = launch_sites_df[['Launch Site', 'Lat', 'Long']]
launch_sites_df

# Start location is NASA Johnson Space Center
nasa_coordinate = [29.559684888503615, -95.0830971930759]
site_map = folium.Map(location=nasa_coordinate, zoom_start=10)

# Create a blue circle at NASA Johnson Space Center's coordinate with a popup label showing its name
circle = folium.Circle(nasa_coordinate, radius=1000, color='#d35400', fill=True).add_child(folium.Popup('NASA Johnson Space Center'))
# Create a blue circle at NASA Johnson Space Center's coordinate with a icon showing its name
marker = folium.map.Marker(
    nasa_coordinate,
    # Create an icon as a text label
    icon=DivIcon(
        icon_size=(20,20),
        icon_anchor=(0,0),
        html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % 'NASA JSC',
        )
    )
site_map.add_child(circle)
site_map.add_child(marker)

site_map=folium.Map(location=[28.5,-80.6],zoom_start=4)
for _,site in launch_sites_df.iterrows():
    coord=[float(site['Lat']),float(site['Long'])]
    folium.Circle(coord,radius=1000,color='#247a68',fill=True,
        popup=site['Launch Site'],tooltip=site['Launch Site']).add_to(site_map)
    folium.Marker(coord,tooltip=site['Launch Site'],popup=site['Launch Site'],
        icon=DivIcon(html=f'<div style="font-size:12px;background:white">{site["Launch Site"]}</div>')).add_to(site_map)
site_map.save(OUT/'01_launch_sites.html')
site_map


spacex_df.tail(10)

marker_cluster = MarkerCluster()


print('Marker colors: success green; failure red.')

# Function to assign color to launch outcome
def assign_marker_color(launch_outcome):
    if launch_outcome == 1:
        return 'green'
    else:
        return 'red'
    
spacex_df['marker_color'] = spacex_df['class'].apply(assign_marker_color)
spacex_df.tail(10)

site_map.add_child(marker_cluster)
for index,record in spacex_df.iterrows():
    folium.Marker([record['Lat'],record['Long']],
        icon=folium.Icon(color='white',icon_color=record['marker_color']),
        tooltip=f"{record['Launch Site']}: landing class {record['class']}",
        popup=f"IBM snapshot record {index}; {record['Launch Site']}; class={record['class']}").add_to(marker_cluster)
site_map.save(OUT/'02_landing_outcomes.html')
site_map


# Add Mouse Position to get the coordinate (Lat, Long) for a mouse over on the map
formatter = "function(num) {return L.Util.formatNum(num, 5);};"
mouse_position = MousePosition(
    position='topright',
    separator=' Long: ',
    empty_string='NaN',
    lng_first=False,
    num_digits=20,
    prefix='Lat:',
    lat_formatter=formatter,
    lng_formatter=formatter,
)

site_map.add_child(mouse_position)
site_map

from math import sin, cos, sqrt, atan2, radians

def calculate_distance(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# Exact coastline example supplied in IBM cell 59; not an independently verified nearest point.
example_coastline=[28.56367,-80.57163]
ksc=launch_sites_df.loc[launch_sites_df['Launch Site'].eq('KSC LC-39A')].iloc[0]
launch_coordinate=[float(ksc['Lat']),float(ksc['Long'])]
distance_coastline=calculate_distance(*launch_coordinate,*example_coastline)
print('Distance to IBM-provided example coastline coordinate, km:',distance_coastline)


folium.Marker(example_coastline,tooltip='IBM example coastline coordinate; nearest status unverified',
 popup=f'Distance from KSC LC-39A to supplied example: {distance_coastline:.3f} km',
 icon=DivIcon(html=f'<div style="background:white;font-size:12px">Example distance {distance_coastline:.2f} km</div>')).add_to(site_map)


lines=folium.PolyLine(locations=[launch_coordinate,example_coastline],weight=2,tooltip='Distance to official example coordinate')
site_map.add_child(lines)

print('Incomplete: closest city, railway and highway coordinates require actual map inspection/source verification. No coordinates invented.')





import json
from geopy.distance import great_circle
marker_count=sum(isinstance(child,folium.Marker) for child in marker_cluster._children.values())
assert marker_count==len(spacex_df)
assert spacex_df['Lat'].between(-90,90).all() and spacex_df['Long'].between(-180,180).all()
assert abs(distance_coastline-great_circle(launch_coordinate,example_coastline).km)<.01
site_map.save(OUT/'03_example_distance_partial.html')
summary={'launch_rows':len(spacex_df),'site_rows':len(launch_sites_df),'cluster_markers':marker_count,'example_distance_km':distance_coastline,'rendered_map_inspected':False,'nearest_coastline_independently_verified':False,'closest_city_railway_highway_completed':False,'example_coordinate_source':'Original IBM notebook cell 59'}
(OUT/'RESULTS.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
