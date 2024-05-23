# modules/map.py

import plotly.graph_objects as go
import math
from shapely import Point, Polygon
from helper import get_coordinates, haversine
from modules.transportDB import TransportDB


# Calculate points for triangle on both sides of the trace between A and B
def calculate_triangle_points(lat_a, lon_a, lat_b, lon_b, angle_deg):
    angle_rad = math.radians(angle_deg)

    delta_lon = lon_b - lon_a
    delta_lat = lat_b - lat_a

    distance = math.sqrt(delta_lat ** 2 + delta_lon ** 2)

    # Angle of trace A-B
    angle_ab = math.atan2(delta_lat, delta_lon)

    # Calculation of coordinate A for triangle
    angle_a = angle_ab + angle_rad
    lat_na = lat_a + distance * math.sin(angle_a)
    lon_na = lon_a + distance * math.cos(angle_a)

    # Calculation of coordinate B for triangle
    angle_b = angle_ab - angle_rad
    lat_nb = lat_a + distance * math.sin(angle_b)
    lon_nb = lon_a + distance * math.cos(angle_b)

    # Return information in tuples
    return (lat_na, lon_na), (lat_nb, lon_nb)


class Map:
    def __init__(self, cities):
        self.cs_dept = cities[0]
        self.cs_dest = cities[1]
        self.cities = TransportDB().cities

        # Calculate triangle points
        self.cs_a, self.cs_b = calculate_triangle_points(self.cs_dept[0], self.cs_dept[1], self.cs_dest[0],
                                                         self.cs_dest[1], 10)

        # Create map
        fig = go.Figure()

        # Add triangles for cone
        fig.add_trace(go.Scattermapbox(
            lat=[self.cs_dept[0], self.cs_a[0], self.cs_dest[0], self.cs_dept[0]],
            lon=[self.cs_dept[1], self.cs_a[1], self.cs_dest[1], self.cs_dept[1]],
            mode='lines+markers',
            fill='toself',
            fillcolor='rgba(0, 0, 0, 0.5)',
            line=dict(width=2, color='black'),
        ))

        fig.add_trace(go.Scattermapbox(
            lat=[self.cs_dept[0], self.cs_b[0], self.cs_dest[0], self.cs_dept[0]],
            lon=[self.cs_dept[1], self.cs_b[1], self.cs_dest[1], self.cs_dept[1]],
            mode='lines+markers',
            fill='toself',
            fillcolor='rgba(0, 0, 0, 0.5)',
            line=dict(width=2, color='black'),
        ))

        # Add departure and destination coordinates as a trace
        fig.add_trace(go.Scattermapbox(
            lon=[self.cs_dept[0], self.cs_dest[0]],
            lat=[self.cs_dept[1], self.cs_dest[1]],
            mode='markers+lines',
            marker=dict(size=20, color=['blue', 'red']),
        ))

        # Update map layout
        fig.update_layout(
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=(self.cs_dept[0] + self.cs_dest[0]) / 2, lon=(self.cs_dept[1] + self.cs_dest[1]) / 2),
                zoom=6
            ),
            showlegend=False
        )

        # Reachable
        self.reacheables = []

        # Check if key cities are within the 20° cone between A and B
        for city in self.cities:
            # Check if cities are within the edges of the polygon
            data = self.check_cities_in_polygon([self.cs_dept, self.cs_a, self.cs_b], city)
            if data:
                self.reacheables.append(data)

        if self.reacheables:
            closest_city = self.get_closest_city()

        # mark reachable cities
        for data in self.reacheables:
            if data["name"] == closest_city[1]:
                fig.add_trace(go.Scattermapbox(
                    lat=[data["latitude"]],
                    lon=[data["longitude"]],
                    mode='markers',
                    fill='toself',
                    fillcolor='rgba(255, 128, 255, 0.5)',
                    marker=dict(size=40, color=['red']),
                ))
            else:
                fig.add_trace(go.Scattermapbox(
                    lat=[data["latitude"]],
                    lon=[data["longitude"]],
                    mode='markers',
                    fill='toself',
                    fillcolor='rgba(255, 128, 255, 0.5)',
                    marker=dict(size=15, color=['blue']),
                ))

        # mark closest city


        fig.show()

    # Check polygon function
    def check_cities_in_polygon(self, edges, city):
        # Create polygon / triangle out of edge-coordinates
        triangle = Polygon(edges)

        # Check if given city is within this polygon / triangle
        if triangle.contains(Point(city["latitude"], city["longitude"])):
            return city

    def get_closest_city(self):
        distances = []

        for cities in self.reacheables:
            distance = haversine(self.cs_dest[0], self.cs_dest[1], cities["latitude"], cities["longitude"])
            distances.append((distance, cities["name"]))

        if distances:
            return min(distances)
        else:
            return None

def main():
    cities = []
    city = ["Bern", "München"]

    for cit in city:
        lat, lon = get_coordinates(cit)
        cities.append((float(lat), float(lon)))

    Map(cities)


if __name__ == '__main__':
    main()
