# modules/transportDB.py

from tinydb import TinyDB, Query
from helper import get_coordinates, get_country_name
from modules.csv_reader import get_countries, get_base_cities
import csv

"""
TODO: 
- change DB in Class TransportDB and change functions into methods
"""

db = TinyDB("TransportDB")
cities = db.table("cities")
countries = db.table("countries")
blacklist = db.table("blacklist")


def add_reachable_cities(name, latitude, longitude, country):
    cities.insert({
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "country": country
    })


def add_countries(german_name, name, main_city, web_link=None):
    countries.insert({
        "german_name": german_name,
        "name": name,
        "main_city": main_city,
        "web_link": web_link
    })


def add_blacklist_entry(departure, arrival, departure_lon, departure_lat, arrival_lon, arrival_lat):
    blacklist.insert({
        "departure": departure,
        "arrival": arrival,
        "departure_cords": {"lon": departure_lon, "lat": departure_lat},
        "arrival_cords": {"lon": arrival_lon, "lat": arrival_lat}
    })


def truncate_table(tablename):
    tablename.truncate()


def fill_cities():
    base_cities = get_base_cities()
    for city in base_cities:
        x, y = get_coordinates(city[0])
        country = get_country_name(x, y)
        add_reachable_cities(city[0], x, y, country)


def fill_countries():
    countries_csv = get_countries()
    for german_name, city, web_link in countries_csv:
        x, y = get_coordinates(city)
        name = get_country_name(x, y)
        add_countries(german_name, name, city, web_link)


def get_web_link(country_name: str):
    """
    retrieves weblink of param country_name (english name) from country database, returns string
    :param country_name:
    :return: string of weblink
    """
    country = Query()
    result = country.search(country.name == country_name)
    return result[0]["web_link"]


def check_blacklist(city1: str, city2: str):
    """
    checks if there has already been blacklist entry for a connection from city1 to city2 and returns the dictionary of
    said connection including the coordinates of the cities (or False if no entry exists).
    :param city1: string of city name
    :param city2: string of city name
    :return: dictionary of connection incl. coordinates of the cities or returns False if no blacklist entry exists
    """
    blacklist = Query()
    result = blacklist.search({blacklist.departure == city1} and blacklist.arrival == city2)
    if result:
        return result
    else:
        return False


def get_cities(city_name):
    city = Query()
    return cities.search(city.name == city_name)


def main():
    truncate_table(cities)
    fill_cities()
    fill_countries()


if __name__ == "__main__":
    main()
