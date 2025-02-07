from geopy.geocoders import Nominatim

def geocode_location(location_name):
    geolocator = Nominatim(user_agent="geo_chatbot", timeout=10)
    location = geolocator.geocode(location_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

# Test
print(geocode_location("Mumbai"))  # Output: (19.0760, 72.8777)