import requests
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString, mapping
import json

# Define Overpass API query to fetch hospitals in Mumbai
overpass_url = "https://overpass-api.de/api/interpreter"
query = """
[out:json];
area["name"="Mumbai"]->.searchArea;
(
  node["amenity"="hospital"](area.searchArea);
  way["amenity"="hospital"](area.searchArea);
  relation["amenity"="hospital"](area.searchArea);
);
out geom;
"""

# Send request
try:
    response = requests.get(overpass_url, params={'data': query})
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
    exit(1)

# Check if data contains elements
if 'elements' not in data or not data['elements']:
    print("No hospital data found.")
    exit(0)

# Process elements into GeoJSON-like features
features = []
for element in data['elements']:
    properties = element.get('tags', {})
    geometry = None
    
    if element['type'] == 'node':
        geometry = Point(element['lon'], element['lat'])
    elif element['type'] == 'way':
        # Ways are linear or polygonal geometries
        if 'geometry' in element:
            coords = [(node['lon'], node['lat']) for node in element['geometry']]
            if len(coords) == 1:  # It's a point if there's only one coordinate
                geometry = Point(coords[0])
            elif len(coords) >= 3:  # Assume it's a polygon if it has 3 or more nodes
                geometry = Polygon(coords)
            else:  # Otherwise, it's a line
                geometry = LineString(coords)
    elif element['type'] == 'relation':
        # Relations are complex and may consist of multiple ways or relations
        # Here we just take the first member for simplicity
        if 'members' in element and element['members']:
            first_member = element['members'][0]
            if 'geometry' in first_member:
                coords = [(node['lon'], node['lat']) for node in first_member['geometry']]
                if len(coords) == 1:
                    geometry = Point(coords[0])
                elif len(coords) >= 3:
                    geometry = Polygon(coords)
                else:
                    geometry = LineString(coords)
    
    if geometry:
        features.append({'type': 'Feature', 'properties': properties, 'geometry': mapping(geometry)})

# Convert features to GeoDataFrame
if features:
    gdf = gpd.GeoDataFrame.from_features(features)
    gdf.to_file("mumbai_hospitals.geojson", driver="GeoJSON")
else:
    print("No valid geometries found.")