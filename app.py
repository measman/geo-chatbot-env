import streamlit as st
from streamlit_folium import st_folium
import folium
from shapely.geometry import Point, Polygon, LineString  # Add this import
from nlp_processor import extract_entities
from geocoder import geocode_location
from gis_processor import find_nearby_places

# Streamlit UI
st.title("🌍 Geospatial Chatbot")
user_query = st.text_input("Ask a question (e.g., 'Find hospitals near Mumbai'):")

if user_query:
    # Step 1: Extract entities
    entities = extract_entities(user_query)
    st.write(f"Detected intent: Find **{entities['place_type']}** near **{entities['location']}**")

    # Step 2: Geocode location
    coordinates = geocode_location(entities['location'])
    if not coordinates:
        st.error("Location not found!")
    else:
        lat, lon = coordinates
        
        # Step 3: Find nearby places
        nearby = find_nearby_places(lat, lon, entities['place_type'])
        
        # Step 4: Show results
        st.success(f"Found **{len(nearby)} {entities['place_type']}s** near **{entities['location']}**")
        
        # Create a map
        m = folium.Map(location=[lat, lon], zoom_start=12)
        for idx, row in nearby.iterrows():
            # st.write(row)
            if isinstance(row.geometry, Point):
                popup_text = row.get('name', row.get('amenity', ''))  # Use 'name' or 'amenity' tag
                # Adding an explicit icon
                folium.Marker(
                    [row.geometry.y, row.geometry.x],
                    popup=popup_text,
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
            elif isinstance(row.geometry, LineString):
                popup_text = row.get('name', row.get('highway', ''))  # Use 'name' or 'highway' tag
                folium.PolyLine(locations=[(point.y, point.x) for point in row.geometry.coords], popup=popup_text).add_to(m)
            elif isinstance(row.geometry, Polygon):
                popup_text = row.get('name', row.get('building', ''))  # Use 'name' or 'building' tag
                folium.Polygon(locations=[(point[1], point[0]) for point in row.geometry.exterior.coords], popup=popup_text).add_to(m)

        st_folium(m, width=700, height=500)
        
        # Optional: Show data table
        st.write(nearby[['name', 'amenity', 'highway', 'building']])  # Customize columns as needed