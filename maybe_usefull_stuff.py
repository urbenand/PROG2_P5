import math
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
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def test_haversine():
    lat1, lon1 = 52.52, 13.405
    lat2, lon2 = 48.137, 11.575
    distance = haversine(lat1, lon1, lat2, lon2)
    print("Distance: {:.2f} km".format(distance))


if __name__ == "__main__":
    test_haversine()
