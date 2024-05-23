from tinydb import TinyDB, Query
from helper import get_coordinates, get_country_name
from modules.csv_reader import get_countries, get_base_cities


class TransportDB:
    def __init__(self, db_path="TransportDB.json"):
        self.db = TinyDB(db_path)
        self.cities = self.db.table("cities")
        self.countries = self.db.table("countries")
        self.blacklist = self.db.table("blacklist")

    def add_reachable_cities(self, name, latitude, longitude, country):
        self.cities.insert({
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "country": country
        })

    def add_countries(self, german_name, name, main_city, web_link=None):
        self.countries.insert({
            "german_name": german_name,
            "name": name,
            "main_city": main_city,
            "web_link": web_link
        })

    def add_blacklist_entry(self, departure, arrival, departure_lon, departure_lat, arrival_lon, arrival_lat):
        self.blacklist.insert({
            "departure": departure,
            "arrival": arrival,
            "departure_cords": {"lon": departure_lon, "lat": departure_lat},
            "arrival_cords": {"lon": arrival_lon, "lat": arrival_lat}
        })

    def truncate_table(self, table_name):
        table = getattr(self, table_name)
        table.truncate()

    def fill_cities(self):
        base_cities = get_base_cities()
        for city in base_cities:
            x, y = get_coordinates(city[0])
            country = get_country_name(x, y)
            self.add_reachable_cities(city[0], x, y, country)

    def fill_countries(self):
        countries_csv = get_countries()
        for german_name, city, web_link in countries_csv:
            x, y = get_coordinates(city)
            name = get_country_name(x, y)
            self.add_countries(german_name, name, city, web_link)

    def get_web_link(self, country_name: str):
        """
        retrieves weblink of param country_name (English name) from country database, returns string
        :param country_name: name of the country in English
        :return: string of weblink
        """
        Country = Query()
        result = self.countries.search(Country.name == country_name)
        return result[0]["web_link"] if result else None

    def check_blacklist(self, city1: str, city2: str):
        """
        checks if there has already been a blacklist entry for a connection from city1 to city2 and returns the dictionary of
        said connection including the coordinates of the cities (or False if no entry exists).
        :param city1: name of the departure city
        :param city2: name of the arrival city
        :return: dictionary of connection incl. coordinates of the cities or returns False if no blacklist entry exists
        """
        Blacklist = Query()
        result = self.blacklist.search((Blacklist.departure == city1) & (Blacklist.arrival == city2))
        return result[0] if result else False

    def get_cities(self, city_name):
        City = Query()
        return self.cities.search(City.name == city_name)

    def main_fill(self):
        self.truncate_table("cities")
        self.fill_cities()
        self.fill_countries()


def main():
    db = TransportDB()
    db.main_fill()
    print(db.get_web_link("Schweiz"))


if __name__ == "__main__":
    main()
