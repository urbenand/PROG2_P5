import math
from geopy.geocoders import Nominatim

"""
for functions or code that may come in handy but has no right place atm

TODO: Check if anything useful can be used in our project
"""


def haversine(lat1, lon1, lat2, lon2):
    """
    the haversine function is used to calculate the distance between to
    locations using the coordinates
    it's pretty accurate and also involves the curving of the earth
    returns km
    """
    R = 6371.0  # Radius of the earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def test_haversine():
    lat1, lon1 = 52.52, 13.405
    lat2, lon2 = 48.137, 11.575
    distance = haversine(lat1, lon1, lat2, lon2)
    print("Distance: {:.2f} km".format(distance))


def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="RudolfUrbenPelichet")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        print("City not found.")
        return None, None

def get_country_name(latitude, longitude):
    geolocator = Nominatim(user_agent="RudolfUrbenPelichet")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    if location:
        address = location.raw.get("address")
        if address:
            country = address.get("country")
            if country:
                country = country.split("/")[0].strip()
            return country



def test_get_coordinates():
    city_name = "Berlin"
    lat, lng = get_coordinates(city_name)
    if lat is not None and lng is not None:
        print(f"Coordinates of {city_name}: Latitude={lat}, Longitude={lng}")


def test_distance_coordianates():
    city1 = "Zürich"
    city2 = "Barcelona"
    lat1, lng1 = get_coordinates(city1)
    print(get_country_name(lat1, lng1))
    lat2, lng2 = get_coordinates(city2)
    print(get_country_name(lat2, lng2))
    distance = haversine(lat1, lng1, lat2, lng2)
    print(f"The Distance between {city1} and {city2} is {distance:.2f}km")


if __name__ == "__main__":
    test_haversine()
    test_get_coordinates()
    test_distance_coordianates()
