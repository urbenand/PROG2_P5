import requests
from datetime import datetime

"""
Class Connections to check the connection and format the response of the website
or just to return the json data
"""


class Connections:
    """
    Initialiser with all Possible values (mandatory and optional) for the request on
    transport.opendata.ch
    """

    def __init__(self, departure=None, destination=None, via=None, date=None, time=None):
        self.url = "https://transport.opendata.ch/v1/connections"  # TODO: Url as static value not class attribute
        self.departure = departure
        self.destination = destination
        self.via = via
        self.date = date
        self.time = time

    def connection_data(self):
        """ connection data updates the URL with the right syntax
        then it will start the request with the updated url and returns the response as a json file
        """
        connection_url = f"{self.url}?from={self.departure}&to={self.destination}"
        if self.via:
            connection_url += f"&via={self.via}"
        if self.date:
            connection_url += f"&date={self.date.strftime('%Y-%m-%d')}"
        if self.time:
            connection_url += f"&time={self.time.strftime('%H:%M')}"
        # implemented Errorhandling for request exceptions
        try:
            response = requests.get(connection_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def check_connection(self):
        """
        gets the Info and extracts departure arrival duration and number of transfers
        out of the Json data
        """
        connection_data = self.connection_data()
        connection_info = []
        if connection_data:
            for connection in connection_data.get("connections", []):
                departure = connection["from"]["departure"]
                arrival = connection["to"]["arrival"]
                duration = connection["duration"]
                transfers = connection["transfers"]

                departure_dt = datetime.fromisoformat(departure)
                arrival_dt = datetime.fromisoformat(arrival)

                connection_info.append((departure_dt, arrival_dt, duration, transfers))
        else:
            print("Failed to retrieve connection information")
        return connection_info


def format_duration(duration_str):
    # Check for correct Format.
    if 'd' in duration_str and ':' in duration_str:
        # extract day and time, then split the time in hours, minutes and seconds
        days, time = duration_str.split("d")
        hours, minutes, seconds = time.split(":")
        # Calculate everything in minutes
        total_minutes = int(days) * 24 * 60 + int(hours) * 60 + int(minutes)
        # convert it into H:M
        formatted_hours = total_minutes // 60
        formatted_minutes = total_minutes % 60
        return f"{formatted_hours}h {formatted_minutes}m"
    else:
        return "Invalid duration format"


def main():
    departure = "Othmarsingen Bahnhof"
    destination = "Zürich HB"
    con = Connections(departure, destination)
    connections_info = con.check_connection()
    print(connections_info)

    if connections_info:
        print("Connection Information:")
        print("{:<40} {:<40} {:<15} {:<10}".format("Departure", "Arrival", "Duration", "Transfers"))
        for connection in connections_info:
            departure = connection[0].strftime("%Y-%m-%d %H:%M:%S %Z")
            arrival = connection[1].strftime("%Y-%m-%d %H:%M:%S %Z")
            duration = format_duration(connection[2])
            transfers = connection[3]
            print("{:<40} {:<40} {:<15} {:<10}".format(departure, arrival, duration, transfers))
    else:
        print("Failed to retrieve connection information")


if __name__ == "__main__":
    main()
