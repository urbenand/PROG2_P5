from tinydb import TinyDB, Query
from maybe_usefull_stuff import get_coordinates, get_country_name
from modules.csv_reader import get_countries, get_base_cities
import csv
"""
TODO: 
- Create a DB search to check if country name is in transport link table
  if True return the transportlink of that city
- implement a Blacklist for already checked connections and the required data
- change DB in Class TransportDB and change functions into methods


"""


db = TinyDB("TransportDB")
cities = db.table("cities")
countries = db.table("countries")
# TODO: Table for machine Lerning


def add_reacheble_cities(name, latitude, longitude, country):
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

def add_Blacklist_entry():
    pass

def truncate_table(tablename):
    tablename.truncate()


def fill_cities():
    base_cities = get_base_cities()
    for city in base_cities:
        x, y = get_coordinates(city[0])
        country = get_country_name(x, y)
        add_reacheble_cities(city[0], x, y, country)


def fill_countries():
    countries_csv = get_countries()
    for german_name, city, web_link in countries_csv:
        x, y = get_coordinates(city)
        name = get_country_name(x, y)
        add_countries(german_name, name, city, web_link)

def get_web_link(city_name):
    pass

def check_blacklist(city1, city2):
    pass

def get_cities(city_name):
    city = Query()
    return cities.search(city.name == city_name)


def main():
    truncate_table(cities)
    fill_cities()
    fill_countries()


if __name__ == "__main__":
    main()