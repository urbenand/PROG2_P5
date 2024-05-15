import requests
import csv

"""
Class to get information about the provided location and stations
and returning the data as json or as a list of all station in the chosen location

TODO: implementing a method to extract location + coordinates 
"""


class Locations:
    def __init__(self, location=None):
        self.url = "https://transport.opendata.ch/v1/locations"  # TODO: make the url a static variable
        self.location = location
        self.stations = []

    def query_location_data(self):
        # Query the data of the chosen location, returning the data in json format
        params = {"query": self.location, "type": "station"}
        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving location data: {e}")
            return None

    def get_station_names(self, loc_data):
        # extract all the station names of the chosen location
        for station in loc_data.get("stations", []):
            self.stations.append(station["name"])

    def print_names(self):
        # Printing out all the stations
        for name in self.stations:
            print(name)

    def choose_station(self):
        # Function to choose a station (probably dont need this)
        for i, station in enumerate(self.stations, start=1):
            print(f"{i} - {station}")

        while True:
            try:
                choice = int(input("Enter Station Number: "))
                if 1 <= choice <= len(self.stations):
                    return self.stations[choice - 1]
                else:
                    print("Invalid Number. Please choose valid station: ")
            except ValueError:
                print("Invalid input. Please enter a number")


def main():
    location = input("Enter Location: ")
    loc = Locations(location)
    loc_data = loc.query_location_data()
    if loc_data:
        loc.get_station_names(loc_data)
        print("Stations in", location + ":")
        loc.print_names()
    else:
        print("Failed to retrieve location data.")
    loc.choose_station()


if __name__ == "__main__":
    main()