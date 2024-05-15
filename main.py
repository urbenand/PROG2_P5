# Main file for INFPROG2 P05 – Individual Application Project
# Variant: Public Transport Routing in Europe

# Authors: Vincent Pelichet, Andreas Rudolf, Andreas Urben

# Imports
from modules import location, connection, UI
import csv


class Application:
    def __init__(self):
        self.key_cities = self.read_key_cities()
        self.connections = connection.Connections()
        self.locations = location.Locations()
        self.ui = UI.MainWindow()

    def read_key_cities(self):
        key_cities = []

        with open("src/cities_stations.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                key_cities.append(row)

        return key_cities


def main():
    app = Application()
    print(app.key_cities)


if __name__ == '__main__':
    main()
