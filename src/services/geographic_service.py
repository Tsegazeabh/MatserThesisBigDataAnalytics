from geopy.geocoders import Nominatim

def get_address_from_GPS(latitude, longitude):
    # Initialize Nominatim geocoder
    geolocator = Nominatim(user_agent="tsegazeabtedla@gmail.com")
    # Combine latitude and longitude into a single string
    location = f"{latitude}, {longitude}"
    # Perform reverse geocoding
    location_info = geolocator.reverse(location, exactly_one=True)
    # Extract address details
    if location_info:
        address = location_info.raw['address']
        return address
    else:
        return None