from tinydb import TinyDB, Query
from helper import get_coordinates, get_country_name
from csv_reader import get_countries, get_base_cities
from connections import Connections


class TransportDB:
    def __init__(self, db_path="TransportDB.json"):
        self.db = TinyDB(db_path)
        self.cities = self.db.table("cities")
        self.countries = self.db.table("countries")
        self.blacklist = self.db.table("blacklist")

        # departure, destination, closest_city, weblink

    def add_reachable_cities(self, name, latitude, longitude, country, reachable):
        self.cities.insert({
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "country": country,
            "reachable": reachable
        })

    def add_countries(self, german_name, name, main_city, web_link=None):
        self.countries.insert({
            "german_name": german_name,
            "name": name,
            "main_city": main_city,
            "web_link": web_link
        })

    def add_blacklist_entry(self, departure, destination, departure_lon, departure_lat, destination_lon,
                            destination_lat, country, weblink, text=""):
        self.blacklist.insert({
            "departure": departure,
            "destination": destination,
            "departure_cords": {"lon": departure_lon, "lat": departure_lat},
            "destination_cords": {"lon": destination_lon, "lat": destination_lat},
            "country": country,
            "weblink": weblink
        })

    def update_blacklist(self, departure, destination, new_text):
        Entry = Query()
        self.blacklist.update({"text": new_text}, (Entry.departure == departure) & (Entry.destination == destination))

    def truncate_table(self, table_name):
        table = getattr(self, table_name)
        table.truncate()

    def fill_cities(self):
        base_cities = get_base_cities()
        for city in base_cities:
            x, y = get_coordinates(city[0])
            country = get_country_name(x, y)
            connection = Connections("Aarau", str(city[0]))
            # TinyDB can't handle bools, so we used strings.
            if connection.check_reachability():
                reachable = "True"
            else:
                reachable = "False"

            self.add_reachable_cities(city[0], x, y, country, reachable)

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
        :param city2: name of the destination city
        :return: dictionary of connection incl. coordinates of the cities or returns False if no blacklist entry exists
        """
        Blacklist = Query()
        result = self.blacklist.search((Blacklist.departure == city1) & (Blacklist.destination == city2))
        return result[0] if result else False

    def get_reachable_cities(self):
        # Directly query the database to retrieve cities where reachable is True
        City = Query()
        # TODO: Change "True" and "False" to 1 / 0, stringcomparison is slow
        return self.cities.search(City.reachable == "True")

    def show_table(self, table_name):
        table = getattr(self, table_name)
        for item in table.all():
            print(item)

    def main_fill(self):
        self.fill_cities()
        self.fill_countries()


def main():
    db = TransportDB()
    # db.truncate_table("blacklist")
    # db.main_fill()
    # print(db.get_web_link("Schweiz"))
    db.show_table("cities")
    db.show_table("countries")
    db.show_table("blacklist")


if __name__ == "__main__":
    main()
