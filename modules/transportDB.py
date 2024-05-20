from tinydb import TinyDB, Query
from maybe_usefull_stuff import get_coordinates, get_country_name
from modules.csv_reader import get_countries, get_base_cities
import csv
"""
TODO: 
- Insert all transport links in transport table
    to do this enter the links in the countries.csv separated by a coma.
    then we can just enter them in the countries table
- Create a DB search to check if country name is in transport link table
  if True return the transportlink of that city
- implement a savingspace for already checked connections and the required data
- change DB in Class TransportDB and change functions into methods


"""


db = TinyDB("TransportDB")
cities = db.table("cities")
countries = db.table("countries")
transport_links = db.table("transport_links")
# TODO: Table for machine Lerning


def add_reacheble_cities(name, latitude, longitude, country):
    cities.insert({
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "country": country
    })


def add_countries(german_name, name, main_city, web_link=None): #delete none when weblinks are in the csv
    countries.insert({
        "german_name": german_name,
        "name": name,
        "main_city": main_city,
        "web_link": web_link
    })


def truncate_table(tablename):
    tablename.truncate()


def get_cities(city_name):
    city = Query()
    return cities.search(city.name == city_name)


def fill_cities():
    base_cities = get_base_cities()
    for city in base_cities:
        x, y = get_coordinates(city[0])
        country = get_country_name(x, y)
        print(city[0], x, y, country)
        add_reacheble_cities(city[0], x, y, country)


def fill_countries():
    countries_csv = get_countries()
    for german_name, city, web_link in countries_csv:
        x, y = get_coordinates(city)
        name = get_country_name(x, y)
        add_countries(german_name, name, city, web_link)


def main():
    truncate_table(cities)
    fill_cities()
    fill_countries()


if __name__ == "__main__":
    main()