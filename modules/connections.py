# modules/connections.py

import requests
from datetime import datetime
from helper import format_duration
from modules.locations import Locations
import pprint


class Connections:
    """
    Class to check the connection and format the response from transport.opendata.ch
    """

    def __init__(self, departure, destination, date=None, time=None):
        self.url = "http://transport.opendata.ch/v1/connections"  # Static URL
        self.departure = departure
        self.destination = destination
        self.date = date
        self.time = time
        self.check_locations()

    def connection_data(self):
        # Fetches connection data from the API and returns the response as a JSON object.
        params = {
            "from": self.departure,
            "to": self.destination,
            "date": self.date if self.date else None,
            "time": self.time if self.time else None
        }

        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def check_locations(self):
        dep_check = Locations(self.departure)
        self.departure = dep_check.check_locations()
        des_check = Locations(self.destination)
        self.destination = des_check.check_locations()

    def check_reachability(self):
        if self.connection_data_extraction():
            return True
        else:
            return False


    def connection_data_extraction(self):
        """
        Extracts and returns relevant information from the connection data.
        """
        data = self.connection_data()
        if not data:
            return None
        connections_info = []

        for connection in data['connections']:
            departure_dt = datetime.fromisoformat(connection["from"]["departure"])
            arrival_dt = datetime.fromisoformat(connection["to"]["arrival"])

            connection_info = {
                'from': {
                    'id': connection['from']['station']['id'],
                    'name': connection['from']['station']['name'],
                    'departure': departure_dt.strftime("%d.%m.%Y %H:%M"),
                    'platform': connection['from']['platform'],
                    'location': connection['from']['location']['coordinate']
                },
                'to': {
                    'id': connection['to']['station']['id'],
                    'name': connection['to']['station']['name'],
                    'arrival': arrival_dt.strftime("%d.%m.%Y %H:%M"),
                    'platform': connection['to']['platform'],
                    'location': connection['to']['location']['coordinate']
                },
                'duration': format_duration(connection['duration']),
                'transfers': connection['transfers'],
                'products': connection['products'],
                'sections': []
            }

            for section in connection['sections']:
                section_info = {}

                if 'journey' in section and section['journey']:
                    journey = section['journey']
                    section_info['journey'] = {
                        'name': journey.get('name'),
                        'category': journey.get('category'),
                        'number': journey.get('number'),
                        'operator': journey.get('operator'),
                        'to': journey.get('to')
                    }

                    if journey['passList']:
                        from_station_info = journey['passList'][0]
                        to_station_info = journey['passList'][-1]

                        from_departure_dt = datetime.fromisoformat(
                            from_station_info.get('departure')) if from_station_info.get('departure') else None
                        to_arrival_dt = datetime.fromisoformat(to_station_info.get('arrival')) if to_station_info.get(
                            'arrival') else None

                        section_info['from'] = {
                            'station_id': from_station_info['station']['id'],
                            'station_name': from_station_info['station']['name'],
                            'departure': from_departure_dt.strftime("%d.%m.%Y %H:%M") if from_departure_dt else None,
                            'platform': from_station_info.get('platform')
                        }

                        section_info['to'] = {
                            'station_id': to_station_info['station']['id'],
                            'station_name': to_station_info['station']['name'],
                            'arrival': to_arrival_dt.strftime("%d.%m.%Y %H:%M") if to_arrival_dt else None,
                            'platform': to_station_info.get('platform')
                        }

                if section.get('walk'):
                    section_info['walk_duration'] = section['walk']['duration']

                connection_info['sections'].append(section_info)

            connections_info.append(connection_info)

        return connections_info


def main():
    departure = "Othmarsingen"
    destination = "Zürich"
    con = Connections(departure, destination, date="2024-05-19", time="10:00")
    print(con.check_reachability())
    connections_info = con.connection_data_extraction()
    pprint.pprint(connections_info)


if __name__ == "__main__":
    main()
