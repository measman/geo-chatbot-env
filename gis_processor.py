import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import transform
import pyproj

def geodesic_buffer(point, radius_km):
    # Create a geodesic buffer
    proj = pyproj.Transformer.from_crs(
        pyproj.CRS("EPSG:4326"),  # WGS84 (lat/lon)
        pyproj.CRS(f"+proj=aeqd +lat_0={point.y} +lon_0={point.x}"),  # Azimuthal equidistant
        always_xy=True
    ).transform
    buffer = transform(proj, point.buffer(radius_km * 1000))  # Radius in meters
    return buffer

def find_nearby_places(lat, lon, data_path="mumbai_hospitals.geojson", place_type="hospital", radius_km=5):
    # Validate latitude and longitude
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError("Invalid latitude or longitude values.")
    
    # Load data
    try:
        data = gpd.read_file(data_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {data_path}")
    
    # Create buffer
    center = Point(lon, lat)
    buffer = geodesic_buffer(center, radius_km)
    
    # Filter using spatial index
    sindex = data.sindex
    possible_matches_index = list(sindex.intersection(buffer.bounds))
    possible_matches = data.iloc[possible_matches_index]
    nearby = possible_matches[possible_matches.geometry.within(buffer)]
    
    return nearby

# Test
mumbai_center = (19.0760, 72.8777)
nearby_hospitals = find_nearby_places(mumbai_center[0], mumbai_center[1])
if nearby_hospitals.empty:
    print("No hospitals found.")
else:
    print(f"Found {len(nearby_hospitals)} hospitals.")
