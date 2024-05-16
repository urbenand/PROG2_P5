from tinydb import TinyDB, Query
from maybe_usefull_stuff import get_coordinates, get_country_name
import csv

db = TinyDB("TransportDB")
cities = db.table("cities")
# TODO: Table for machine Lerning

def add_cities(name, latitude, longitude, country):
    cities.insert({
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "country": country
    })

def truncate_table():
    cities.truncate()


def get_cities(city_name):
    city = Query()
    return cities.search(city.name == city_name)


base_cities = []

with open("cities.csv", "r", encoding="utf-8",) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        base_cities.append(row)
    print(cities)


def fill_db():
    for city in base_cities:
        x, y = get_coordinates(city[0])
        country = get_country_name(x, y)
        print(city[0], x, y, country)
        add_cities(city[0], x, y, country)


def main():
    truncate_table()
    fill_db()


if __name__ == "__main__":
    main()