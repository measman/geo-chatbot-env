import geopandas as gpd
from shapely.geometry import Point

def find_nearby_places(lat, lon, place_type, radius_km=5):
    # Load hospitals data
    hospitals = gpd.read_file("mumbai_hospitals.geojson")
    
    # Create a buffer (approx. 5 km in degrees)
    center = Point(lon, lat)
    buffer = center.buffer(radius_km * 0.009)  # ~1 km ≈ 0.009 degrees
    
    # Filter hospitals within the buffer
    nearby = hospitals[hospitals.geometry.within(buffer)]
    return nearby

# Test
mumbai_center = (19.0760, 72.8777)
nearby_hospitals = find_nearby_places(mumbai_center[0], mumbai_center[1], "hospital")
print(f"Found {len(nearby_hospitals)} hospitals.")