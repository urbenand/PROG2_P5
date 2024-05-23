import requests
from translate import Translator
from langdetect import detect
from collections import Counter
import re

"""
Class to get information about the provided location and stations
and retruning the data as json or as a list of all station in the chosen location
"""


class Locations:
    def __init__(self, location=None, lat=None, lng=None):
        self.url = "http://transport.opendata.ch/v1/locations"
        self.location = location
        self.lat = lat
        self.lng = lng
        self.stations = []

    def query_location_data(self):
        # Query the data of the chosen location, returning the data in json format
        params = {}
        if self.lat:
            params["x"] = self.lat
        if self.lng:
            params["y"] = self.lng
        else:
            params = {"query": self.location, "type": "station"}
        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving location data: {e}")
            return None

    def check_german(self):
        check_list = []
        for station in self.stations:
            check_list.append(detect(station))
        counter = Counter(check_list)
        most_language, _ = counter.most_common(1)[0]
        return most_language

    def split_station_names(self, text):
        # Regex pattern to split by space, slash, and any other desired delimiters
        pattern = r'[\/-]'  # Hier kannst du weitere Trennzeichen hinzufügen, falls nötig
        return re.split(pattern, text)

    def check_locations(self):
        self.get_station_names(self.query_location_data())
        language_name = self.check_german()
        translator = Translator(from_lang="de", to_lang=language_name)
        check_location = translator.translate(self.location)
        for station in self.stations:
            station_separated_special = self.split_station_names(station)
            station_separated = station.split()
            if station_separated[0].lower() == check_location.lower():
                return station
            else:
                if station_separated_special[0].lower() or station_separated_special[
                    1].lower() == check_location.lower():
                    return station
        return None

    def get_station_names(self, loc_data):
        # Extract all the station names from the given JSON data and add them to self.stations
        for station in loc_data.get("stations", []):
            self.stations.append(station["name"])


def main():
    location = input("Enter Location: ")
    loc = Locations(location)
    loc_data = loc.query_location_data()
    print(loc_data)
    loc.get_station_names(loc_data)
    print(loc.check_locations())
    print(loc.check_german())
    print(loc.stations)


if __name__ == "__main__":
    main()
