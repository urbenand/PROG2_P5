# modules/helper.py

import math
from geopy.geocoders import Nominatim
import re

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


def test_distance_coordinates():
    city1 = "Zürich"
    city2 = "Barcelona"
    lat1, lng1 = get_coordinates(city1)
    print(get_country_name(lat1, lng1))
    lat2, lng2 = get_coordinates(city2)
    print(get_country_name(lat2, lng2))
    distance = haversine(lat1, lng1, lat2, lng2)
    print(f"The Distance between {city1} and {city2} is {distance:.2f}km")


def format_duration(duration):
    match = re.match(r"(\d+)d(\d+):(\d+):(\d+)", duration)
    if not match:
        return duration

    days, hours, minutes, seconds = map(int, match.groups())
    total_minutes = days * 24 * 60 + hours * 60 + minutes

    if total_minutes // 60 == 0:
        formatted_duration = f"{total_minutes % 60} min."
    else:
        formatted_duration = f"{total_minutes // 60} Hours {total_minutes % 60} min."

    return formatted_duration


# Funktion zur Berechnung der neuen Punkte im 10° Winkel nördlich und südlich der Linie A-B
def calculate_triangle_points(lat1, lon1, lat2, lon2, angle_deg):
    angle_rad = math.radians(angle_deg)
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    distance = math.sqrt(delta_lat ** 2 + delta_lon ** 2)

    # Winkel der Linie A-B
    angle_AB = math.atan2(delta_lat, delta_lon)

    # Berechnung der nördlichen Koordinate
    angle_N = angle_AB + angle_rad
    lat_N = lat1 + distance * math.sin(angle_N)
    lon_N = lon1 + distance * math.cos(angle_N)

    # Berechnung der südlichen Koordinate
    angle_S = angle_AB - angle_rad
    lat_S = lat1 + distance * math.sin(angle_S)
    lon_S = lon1 + distance * math.cos(angle_S)

    return (lat_N, lon_N), (lat_S, lon_S)


def percent_calculator(reachable_distance, leftover_distance):
    full_distance = reachable_distance + leftover_distance
    reachable_percent = 100 / full_distance * reachable_distance
    leftover_percent = 100 / full_distance * leftover_distance
    return full_distance, reachable_percent, leftover_percent


if __name__ == "__main__":
    test_haversine()
    test_get_coordinates()
    test_distance_coordinates()
