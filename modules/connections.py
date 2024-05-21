import requests
from datetime import datetime
from helper import format_duration


class Connections:
    """
    Class to check the connection and format the response from transport.opendata.ch
    """

    def __init__(self, departure, destination, date, time):
        self.url = "https://transport.opendata.ch/v1/connections"  # Static URL
        self.departure = departure
        self.destination = destination
        self.date = date
        self.time = time

    def connection_data(self):
        """
        Fetches connection data from the API and returns the response as a JSON object.
        """
        params = {
            "from": self.departure,
            "to": self.destination,
            "date": self.date,
            "time": self.time
        }

        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

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
                    'coordinate': connection['from']['station']['coordinate'],
                    'name': connection['from']['station']['name'],
                    'departure': departure_dt.strftime("%d.%m.%Y %H:%M"),
                    'platform': connection['from']['platform'],
                },
                'to': {
                    'id': connection['to']['station']['id'],
                    'coordinate': connection['to']['station']['coordinate'],
                    'name': connection['to']['station']['name'],
                    'delay': connection['to']['station']['delay'],
                    'arrival': arrival_dt.strftime("%d.%m.%Y %H:%M"),
                    'platform': connection['to']['platform']
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

                if section.get('walk'):
                    section_info['walk_duration'] = section['walk']['duration']

                departure = section['departure']
                sec_dep_dt = datetime.fromisoformat(departure["departure"])
                section_info['departure'] = {
                    'station_id': departure['station']['id'],
                    'station_name': departure['station']['name'],
                    'departure': sec_dep_dt.strftime("%d.%m.%Y %H:%M"),
                }

                if 'arrival' in section:
                    arrival = section['arrival']
                    sec_arr_dt = datetime.fromisoformat(arrival["arrival"])
                    section_info['arrival'] = {
                        'station_id': arrival['station']['id'],
                        'station_name': arrival['station']['name'],
                        'arrival': sec_arr_dt.strftime("%d.%m.%Y %H:%M"),
                    }

                connection_info['sections'].append(section_info)

            connections_info.append(connection_info)

        return connections_info

def main():
    departure = "Zürich"
    destination = "Othmarsingen"
    con = Connections(departure, destination, date="2024-05-19", time="10:00")
    con_data = con.connection_data()
    print(con_data)
    connections_info = con.connection_data_extraction()

    if not connections_info:
        print("No connections found.")
        return None

    for connection_info in connections_info:
        print("From:")
        print(f"  ID: {connection_info['from']['id']}")
        print(f"  Name: {connection_info['from']['name']}")
        print(f"  Departure: {connection_info['from']['departure']}")

        print("\nTo:")
        print(f"  ID: {connection_info['to']['id']}")
        print(f"  Name: {connection_info['to']['name']}")
        print(f"  Arrival: {connection_info['to']['arrival']}")
        print(f"  Platform: {connection_info['to']['platform']}")

        print(f"\nDuration: {connection_info['duration']}")
        print(f"Transfers: {connection_info['transfers']}")
        print(f"Products: {', '.join(connection_info['products'])}")

        print("\nSections:")
        for section in connection_info['sections']:
            if 'journey' in section:
                journey = section['journey']
                print(f"  Journey:")
                print(f"    Name: {journey['name']}")
                print(f"    Category: {journey['category']}")
                print(f"    Number: {journey['number']}")
                print(f"    Operator: {journey['operator']}")
                print(f"    To: {journey['to']}")

            if 'walk_duration' in section:
                print(f"  Walk Duration: {section['walk_duration']} seconds")

            print("  Departure:")
            departure = section['departure']
            print(f"    Station ID: {departure['station_id']}")
            print(f"    Station Name: {departure['station_name']}")
            print(f"    Departure: {departure['departure']}")

            if 'arrival' in section:
                print("  Arrival:")
                arrival = section['arrival']
                print(f"    Station ID: {arrival['station_id']}")
                print(f"    Station Name: {arrival['station_name']}")
                print(f"    Arrival: {arrival['arrival']}")

if __name__ == "__main__":
    main()
