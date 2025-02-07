import streamlit as st
from streamlit_folium import st_folium
import folium
from shapely.geometry import Point, Polygon, LineString  # Add this import
from nlp_processor import extract_entities
from geocoder import geocode_location
from gis_processor import find_nearby_places

@st.cache_data
def get_nearby(lat, lon, place_type):
    return find_nearby_places(lat, lon, place_type)

st.title("🌍 Geospatial Chatbot")
user_query = st.text_input("Ask a question (e.g., 'Find hospitals near Mumbai'):")

# Always display the search button
search_clicked = st.button("Search")

# Initialize session state for storing search results
if "results" not in st.session_state:
    st.session_state.results = None

if search_clicked:
    if not user_query:
        st.warning("Please enter a query!")
    else:
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
            nearby = get_nearby(lat, lon, entities['place_type'])

            # Store results in session state so they persist across reruns
            st.session_state.results = {"lat": lat, "lon": lon, "entities": entities, "nearby": nearby}

if st.session_state.results:
    lat = st.session_state.results["lat"]
    lon = st.session_state.results["lon"]
    entities = st.session_state.results["entities"]
    nearby = st.session_state.results["nearby"]

    st.success(f"Found **{len(nearby)} {entities['place_type']}s** near **{entities['location']}**")

    # Create a map
    m = folium.Map(location=[lat, lon], zoom_start=12)
    for idx, row in nearby.iterrows():
        if isinstance(row.geometry, Point):
            popup_text = row.get('name', row.get('amenity', ''))
            folium.Marker(
                [row.geometry.y, row.geometry.x],
                popup=popup_text,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
        elif isinstance(row.geometry, LineString):
            popup_text = row.get('name', row.get('highway', ''))
            folium.PolyLine(
                locations=[(point.y, point.x) for point in row.geometry.coords],
                popup=popup_text
            ).add_to(m)
        elif isinstance(row.geometry, Polygon):
            popup_text = row.get('name', row.get('building', ''))
            folium.Polygon(
                locations=[(point[1], point[0]) for point in row.geometry.exterior.coords],
                popup=popup_text
            ).add_to(m)

    st_folium(m, width=700, height=500)
    
    # Optional: Show data table with only available columns
    desired_cols = ['name', 'amenity', 'highway', 'building']
    existing_cols = [col for col in desired_cols if col in nearby.columns]
    if existing_cols:
        st.write(nearby[existing_cols])
    else:
        st.write(nearby)