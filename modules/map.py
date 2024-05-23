# modules/map.py

import plotly.graph_objects as go
import math
from shapely import Point, Polygon
from helper import get_coordinates
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
        cs_dept = cities[0]
        cs_dest = cities[1]
        self.cities = TransportDB().cities

        # Calculate triangle points
        cs_a, cs_b = calculate_triangle_points(cs_dept[0], cs_dept[1], cs_dest[0], cs_dest[1], 10)

        # Create map
        fig = go.Figure()

        # Add triangles for cone
        fig.add_trace(go.Scattermapbox(
            lat=[cs_dept[0], cs_a[0], cs_dest[0], cs_dept[0]],
            lon=[cs_dept[1], cs_a[1], cs_dest[1], cs_dept[1]],
            mode='lines+markers',
            fill='toself',
            fillcolor='rgba(0, 0, 0, 0.5)',
            line=dict(width=2, color='black'),
        ))

        fig.add_trace(go.Scattermapbox(
            lat=[cs_dept[0], cs_b[0], cs_dest[0], cs_dept[0]],
            lon=[cs_dept[1], cs_b[1], cs_dest[1], cs_dept[1]],
            mode='lines+markers',
            fill='toself',
            fillcolor='rgba(0, 0, 0, 0.5)',
            line=dict(width=2, color='black'),
        ))

        # Add departure and destination coordinates as a trace
        fig.add_trace(go.Scattermapbox(
            lon=[cs_dept[0], cs_dest[0]],
            lat=[cs_dept[1], cs_dest[1]],
            mode='markers+lines',
            marker=dict(size=20, color=['blue', 'red']),
        ))

        # Update map layout
        fig.update_layout(
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=(cs_dept[0] + cs_dest[0]) / 2, lon=(cs_dept[1] + cs_dest[1]) / 2),
                zoom=6
            ),
        )

        for city in self.cities:
            # Check if cities are within the edges of the polygon
            name = self.check_cities_in_polygon([cs_dept, cs_a, cs_b], city)

            if name:
                print(name)
                fig.add_trace(go.Scattermapbox(
                    lat=[city["latitude"]],
                    lon=[city["longitude"]],
                    mode='markers',
                    fill='toself',
                    fillcolor='rgba(255, 128, 255, 0.5)',
                    marker=dict(size=15, color=['blue', 'red']),
                ))

        fig.show()

    def check_cities_in_polygon(self, edges, city):
        # Create polygon / triangle out of edge-coordinates
        triangle = Polygon(edges)

        # Check if given city is within this polygon / triangle
        if triangle.contains(Point(city["latitude"], city["longitude"])):
            return city["name"]


def main():
    cities = []
    city = ["Genf", "Berlin Hbf"]

    for cit in city:
        lat, lon = get_coordinates(cit)
        cities.append((float(lat), float(lon)))

    print(cities)
    Map(cities)


if __name__ == '__main__':
    main()
